import boto3
import os
import json
import streamlit as st

def get_bedrock_client():
    """Create AWS Bedrock client with error handling."""
    try:
        return boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    except Exception as e:
        st.error(f"Error creating Bedrock client: {str(e)}")
        st.stop()

def get_titan_embedding(text, bedrock_client):
    """Use Amazon Titan for text embeddings with robust error handling."""
    try:
        body = json.dumps({"inputText": text})
        response = bedrock_client.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=body,
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read().decode('utf-8'))
        return response_body['embedding']
    except Exception as e:
        st.warning(f"Embedding generation error: {str(e)}")
        return None