from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Claim(BaseModel):
    text: str
    status: str
    reason: str

class Citation(BaseModel):
    text: str
    status: str
    reason: str

class VerificationResult(BaseModel):
    score: int
    summary: str
    claims: List[Claim]
    citations: List[Citation]

class VerificationCreate(BaseModel):
    text: str

class VerificationResponse(BaseModel):
    id: int
    input_text: str
    result: VerificationResult
    created_at: datetime

    class Config:
        from_attributes = True
