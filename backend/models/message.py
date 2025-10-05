from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class MessageBase(BaseModel):
    text: str
    message_type: str = "text"  # text, image, file

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    chat_id: str
    sender_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "sent"  # sent, delivered, read
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    sender_id: str
    text: str
    timestamp: datetime
    status: str
    message_type: str
    created_at: datetime

    class Config:
        allow_population_by_field_name = True

class MessageStatusUpdate(BaseModel):
    status: str  # delivered, read