from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON, Relationship

class Verification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    input_text: str
    result: Dict[str, Any] = Field(sa_column=Column(JSON)) # score, summary, claims, citations
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str # "user" or "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    conversation: Conversation = Relationship(back_populates="messages")