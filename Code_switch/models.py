from pydantic import BaseModel


# Model for the detect language request body
class DetectLanguageRequest(BaseModel):
    code: str


# Model for the detect language response body
class DetectLanguageResponse(BaseModel):
    detected_language: str


# Model for the convert_code request body
class CodeRequest(BaseModel):
    source_code: str
    target_language: str


# Model for the convert_code response body
class CodeResponse(BaseModel):
    converted_code: str


# Model for the generate_documentation request body
class DocumentationRequest(BaseModel):
    code: str
    language: str


# Model for the generate_documentation response body
class DocumentationResponse(BaseModel):
    documentation: str


# Model for the check_syntax request body
class SyntaxRequest(BaseModel):
    code: str
    language: str


# Model for the check_syntax response body
class SyntaxResponse(BaseModel):
    result: str
