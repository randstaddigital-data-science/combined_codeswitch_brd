import boto3
import json
from pdf2image import convert_from_path
from byaldi import RAGMultiModalModel
import os
from dotenv import load_dotenv
import base64
from io import BytesIO
from functools import lru_cache
import botocore.exceptions
import time

load_dotenv()  # Load environment variables from .env file

class RAGClaudeProcessor:
    def __init__(self):
        self.initialize_rag_engine()
        # Initialize the AWS Bedrock client
        self.bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.indexed_pdf = None
        self.pdf_images = None

    def initialize_rag_engine(self):
        # Load the RAG engine model
        self.rag_engine = RAGMultiModalModel.from_pretrained("vidore/colpali")

    @lru_cache(maxsize=10)
    def index_pdf(self, pdf_path):
        if self.indexed_pdf != pdf_path:
            # Reinitialize the RAG engine to reset the index
            self.initialize_rag_engine()

            # Index the document
            self.rag_engine.index(
                input_path=pdf_path,
                index_name="index",
                store_collection_with_index=False,
                overwrite=True
            )

            # Convert PDF to images
            self.pdf_images = convert_from_path(pdf_path)
            self.indexed_pdf = pdf_path

    def process_query(self, query):
        if not self.indexed_pdf:
            raise ValueError("No PDF has been indexed. Please upload and index a PDF first.")

        # Perform RAG search
        results = self.rag_engine.search(query, k=3)
        if not results:
            raise ValueError("No results found from the RAG search.")

        # Safely access 'content' as an attribute
        rag_context = "\n".join([getattr(result, 'content', 'No content available') for result in results])

        # Ensure results contain a valid page number
        image_index = getattr(results[0], "page_num", 1) - 1  # Default to first page if 'page_num' is missing
        if image_index >= len(self.pdf_images) or image_index < 0:
            raise IndexError("Invalid page number returned from RAG search.")

        # Construct prompt with RAG results
        full_prompt = f"""
        You are tasked with answering a query strictly based on the content from the uploaded document. The document provides specific technical information and context, and your response must consider all relevant details, specifications, and technicalities mentioned.

        Context from the document:
        {rag_context}

        Please answer the following question, using only the information from the document. Where required, structure the response clearly in points or steps:

        Question: {query}

        Response:
        - Ensure to cover all technical aspects and details provided in the context.
        - Break down the answer into points or steps wherever necessary to ensure clarity and completeness.
        - Provide a concise but comprehensive explanation based solely on the provided content.
        """

        # Query Claude with the constructed prompt and relevant image
        return self.query_claude_with_retry(full_prompt, self.pdf_images[image_index])

    def query_claude_with_retry(self, prompt, image, retries=3, delay=2):
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Prepare the payload for Claude
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        for attempt in range(retries):
            try:
                # Make the API call to AWS Bedrock
                response = self.bedrock.invoke_model(
                    modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
                    body=json.dumps(payload)
                )
                # Parse and return the response
                response_body = json.loads(response['body'].read())
                return response_body['content'][0]['text']
            except botocore.exceptions.ClientError as e:
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    raise RuntimeError(f"Error while querying Claude: {e}")