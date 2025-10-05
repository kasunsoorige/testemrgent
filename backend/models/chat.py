from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class LastMessage(BaseModel):
    text: str
    sender_id: str
    timestamp: datetime
    status: str = "sent"  # sent, delivered, read

class ChatBase(BaseModel):
    participants: List[str]
    type: str = "private"  # private or group
    is_pinned: bool = False

class ChatCreate(ChatBase):
    pass

class Chat(ChatBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    last_message: Optional[LastMessage] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True

class ChatResponse(BaseModel):
    id: str
    participants: List[str]
    type: str
    last_message: Optional[LastMessage]
    is_pinned: bool
    created_at: datetime
    participant_details: Optional[List[dict]] = None

    class Config:
        allow_population_by_field_name = True