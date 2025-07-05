from pydantic import BaseModel

class RefactorResponse(BaseModel):
    refactored_code: str
    logs: str
    framework: str
    version: str