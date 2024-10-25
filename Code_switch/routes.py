from fastapi import APIRouter, HTTPException, Query
from models import (
    DetectLanguageRequest,
    DetectLanguageResponse,
    CodeRequest,
    CodeResponse,
    DocumentationRequest,
    DocumentationResponse,
    SyntaxRequest,
    SyntaxResponse,
)
from functions import convert_code, generate_documentation, check_syntax
from language_detection import detect_language

router = APIRouter()


@router.post("/detect_language", response_model=DetectLanguageResponse)
def detect_language_endpoint(request: DetectLanguageRequest):
    detected_language = detect_language(request.code)
    return DetectLanguageResponse(detected_language=detected_language)


@router.post("/convert", response_model=CodeResponse)
def convert_code_endpoint(
    request: CodeRequest,
    target_language: str = Query(
        ...,
        title="Target Language",
        description="Select the target language for code conversion",
        enum=["Python", "Java", "C++", "COBOL"],
    ),
):
    try:
        source_language = detect_language(request.source_code)
        if source_language == "Unknown":
            raise HTTPException(
                status_code=400, detail="Could not detect the source language."
            )
        converted_code = convert_code(
            request.source_code, source_language, request.target_language
        )
        return CodeResponse(converted_code=converted_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) @ router.post(
            "/generate_documentation", response_model=DocumentationResponse
        )


def generate_documentation_endpoint(request: DocumentationRequest):
    try:
        documentation = generate_documentation(request.code, request.language)
        return DocumentationResponse(documentation=documentation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/convert_and_document", response_model=DocumentationResponse)
def convert_and_document_endpoint(
    request: CodeRequest,
    target_language: str = Query(
        ...,
        title="Target Language",
        description="Select the target language for code conversion",
        enum=["Python", "Java", "C++", "COBOL"],
    ),
):
    try:
        source_language = detect_language(request.source_code)
        if source_language == "Unknown":
            raise HTTPException(
                status_code=400, detail="Could not detect the source language."
            )
        converted_code = convert_code(
            request.source_code, source_language, target_language
        )
        documentation = generate_documentation(converted_code, target_language)
        return DocumentationResponse(documentation=documentation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/check_syntax", response_model=SyntaxResponse)
def check_syntax_endpoint(request: SyntaxRequest):
    try:
        result = check_syntax(request.code, request.language)
        return SyntaxResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
