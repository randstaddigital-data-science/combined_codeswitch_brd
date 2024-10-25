import os
import json
import re
import subprocess
import ast, boto3
import requests
from langchain_community.llms import Bedrock
from dotenv import load_dotenv
from code_switch.prompts import get_conversion_prompt, get_documentation_prompt

load_dotenv()


def get_bedrock_client():
    return boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


def get_custom_llm():
    model_id = "mistral.mistral-large-2402-v1:0"
    model_kwargs = {
        "max_tokens": 2048,
        "temperature": 0.3,
        "top_k": 50,
        "top_p": 0.9,
    }
    client = get_bedrock_client()
    custom_llm = Bedrock(client=client, model_id=model_id, model_kwargs=model_kwargs)
    return custom_llm


def convert_code(code, source_language, target_language):
    custom_llm = get_custom_llm()
    prompt = get_conversion_prompt(source_language, target_language, code)
    response = custom_llm(prompt)
    print("Convert Response:", response)  # Debugging
    try:
        response_dict = json.loads(response)
        if "text" in response_dict:
            return response_dict["text"]
        else:
            print("Error: 'text' key not found in the response.")
            return "Error: 'text' key not found in the response."
    except json.JSONDecodeError:
        print("Convert Response is not JSON. Returning raw response.")
        return response


def generate_documentation(code, language):
    custom_llm = get_custom_llm()
    prompt = get_documentation_prompt(language, code)
    response = custom_llm(prompt)
    print("Documentation Response:", response)  # Debugging
    try:
        response_dict = json.loads(response)
        if "text" in response_dict:
            return response_dict["text"]
        else:
            print("Error: 'text' key not found in the response.")
            return "Error: 'text' key not found in the response."
    except json.JSONDecodeError:
        print("Documentation Response is not JSON. Returning raw response.")
        return response


def check_syntax_cpp(code):
    with open("temp.cpp", "w") as f:
        f.write(code)
    result = subprocess.run(
        ["g++", "-fsyntax-only", "temp.cpp"], capture_output=True, text=True
    )
    return result.returncode == 0, result.stderr


def check_syntax_cobol(code):
    with open("temp.cob", "w") as f:
        f.write(code)
    result = subprocess.run(
        ["cobc", "-fsyntax-only", "temp.cob"], capture_output=True, text=True
    )
    return result.returncode == 0, result.stderr


def extract_code(text):
    """
    Extracts the actual code from the provided text, assuming the code is enclosed in a markdown code block or similar structure.
    """
    code_block_pattern = (
        r"```(?:\w+\n)?(.*?)```"  # Regex to extract code within triple backticks
    )
    code_match = re.search(code_block_pattern, text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    return text.strip()


def check_syntax_python(code):
    try:
        ast.parse(code)
        return "Syntax Check Complete: Correct."
    except SyntaxError as e:
        return f"Syntax error: {e}"


def check_syntax_java_(code):
    with open("temp.java", "w") as f:
        f.write(code)
    lint_result = subprocess.run(
        [
            "java",
            "-jar",
            "checkstyle-8.45-all.jar",
            "-c",
            "/google_checks.xml",
            "temp.java",
        ],
        capture_output=True,
        text=True,
    )
    format_result = subprocess.run(
        [
            "java",
            "-jar",
            "google-java-format-1.9-all-deps.jar",
            "--dry-run",
            "--set-exit-if-changed",
            "temp.java",
        ],
        capture_output=True,
        text=True,
    )
    os.remove("temp.java")
    lint_output = (
        lint_result.stdout if lint_result.returncode == 0 else lint_result.stderr
    )
    format_output = (
        format_result.stdout if format_result.returncode == 0 else format_result.stderr
    )
    return lint_output, format_output


def check_syntax_java(code):

    patterns = [
        r"public\s+class\s+\w+\s*\{",  # public class ClassName {
        r"public\s+static\s+void\s+main\s*\(String\[\]\s+\w+\)\s*\{",  # public static void main(String[] args) {
        r"public\s+\w+\s*\(\s*\)\s*\{",  # public Constructor() {
        r"public\s+\w+\s+\w+\s*\(\s*\)\s*\{",  # public ReturnType methodName() {
    ]

    for pattern in patterns:
        if re.search(pattern, code):
            return " Evaluation Complete: Syntax is Correct."

    return "Syntax Incorrect."


def check_syntax(code, language):
    code = extract_code(code)
    if language.lower() == "python":
        return check_syntax_python(code)
    elif language.lower() == "java":
        return check_syntax_java(code)
    else:
        return "Syntax check not available for this langauge"
