from pydantic import BaseModel
from typing import Dict, Any

class AnalysisResponse(BaseModel):
    analysis: Dict[str, Any]
    framework: str
    version: str