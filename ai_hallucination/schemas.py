from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

# --- Verification Schemas ---
class Claim(BaseModel):
    text: string
    status: str  # verified, questionable, false
    reason: str

class Citation(BaseModel):
    text: string
    status: str  # valid, invalid, unknown
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

# --- Chat Schemas ---
class MessageCreate(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True

# --- Image Schemas ---
class ImageRequest(BaseModel):
    prompt: str
    size: Optional[str] = "1024x1024"

class ImageResponse(BaseModel):
    url: str
    b64_json: Optional[str] = None