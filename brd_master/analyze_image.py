import base64
import json
import os
import time  # Added for timing
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
from dotenv import load_dotenv
import aiohttp
import traceback  # For detailed error traceback

# Import Prometheus metrics

from brd_master.metrics import metrics

# Load environment variables from .env file
load_dotenv()


async def check_guardrails(session, guardrail_id, input_text):
    try:
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        region = os.getenv("AWS_REGION")

        credentials = Credentials(
            access_key=aws_access_key_id, secret_key=aws_secret_access_key
        )

        url = f"https://bedrock.{region}.amazonaws.com/agents/guardrails/{guardrail_id}/evaluations"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        request_body = {"inputText": input_text}

        request = AWSRequest(
            method="POST", url=url, data=json.dumps(request_body), headers=headers
        )
        SigV4Auth(credentials, "bedrock", region).add_auth(request)

        async with session.post(
            url, data=request.body, headers=dict(request.headers)
        ) as response:
            response_body = await response.json()
            return response_body.get("results", [])

    except Exception as e:
        print(f"An error occurred while checking guardrails: {e}")
        return None


async def analyze_image(session, model_id, image_data, page_num):
    start_time = time.time()  # Start timing the analysis duration
    try:
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        # Read the prompt from the file
        with open("brd_master/prompt.txt", "r") as file:
            prompt = file.read().format(page_num=page_num)

        # Get the Guardrail ID from environment variables
        guardrail_id = os.getenv("GUARDRAIL_ID")
        if not guardrail_id:
            raise ValueError("Guardrail ID is not set in environment variables.")

        # Check guardrails
        guardrail_results = await check_guardrails(session, guardrail_id, prompt)
        if guardrail_results is None:
            metrics.analysis_errors.inc()  # Increment error counter
            return page_num, "Error checking guardrails"

        # If guardrails failed, return without invoking the model
        if any(result.get("evaluation") == "FAIL" for result in guardrail_results):
            metrics.analysis_errors.inc()  # Increment error counter
            return page_num, "Content blocked by guardrails"

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": encoded_image,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        }

        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        region = os.getenv("AWS_REGION")

        credentials = Credentials(
            access_key=aws_access_key_id, secret_key=aws_secret_access_key
        )

        url = f"https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/invoke"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        request = AWSRequest(
            method="POST", url=url, data=json.dumps(request_body), headers=headers
        )
        SigV4Auth(credentials, "bedrock", region).add_auth(request)

        async with session.post(
            url, data=request.body, headers=dict(request.headers)
        ) as response:
            response_body = await response.json()
            content = response_body.get("content", [{}])[0].get("text", "No content")

            if not content or content == "No content":
                print(
                    f"Page {page_num} - Full Response: {json.dumps(response_body, indent=2)}"
                )

            metrics.analyzed_pages.inc()  # Increment analyzed pages counter
            return page_num, content

    except Exception as e:
        print(f"An error occurred while processing page {page_num}: {e}")
        traceback.print_exc()
        metrics.analysis_errors.inc()  # Increment error counter
        return page_num, None

    finally:
        duration = time.time() - start_time
        metrics.analysis_duration.observe(duration)  # Record analysis duration
