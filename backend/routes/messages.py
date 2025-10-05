from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from models.message import MessageCreate, Message, MessageResponse, MessageStatusUpdate
from models.chat import LastMessage
from auth.auth_handler import auth_handler
from database import db
from datetime import datetime

router = APIRouter(prefix="/chats", tags=["messages"])

@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: str,
    user_id: str = Depends(auth_handler.auth_wrapper),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get messages for a specific chat"""
    
    # Verify user has access to chat
    chat_doc = await db.chats.find_one({"_id": chat_id})
    
    if not chat_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    if user_id not in chat_doc["participants"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this chat"
        )
    
    # Get messages with pagination (newest first)
    messages_cursor = db.messages.find({"chat_id": chat_id}).sort("timestamp", -1).skip(offset).limit(limit)
    messages = await messages_cursor.to_list(limit)
    
    # Convert to response format and reverse to show oldest first
    message_responses = []
    for msg_doc in reversed(messages):
        message_responses.append(MessageResponse(
            id=msg_doc["_id"],
            chat_id=msg_doc["chat_id"],
            sender_id=msg_doc["sender_id"],
            text=msg_doc["text"],
            timestamp=msg_doc["timestamp"],
            status=msg_doc["status"],
            message_type=msg_doc["message_type"],
            created_at=msg_doc["created_at"]
        ))
    
    return message_responses

@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: str,
    message_data: MessageCreate,
    user_id: str = Depends(auth_handler.auth_wrapper)
):
    """Send a message to a chat"""
    
    # Verify user has access to chat
    chat_doc = await db.chats.find_one({"_id": chat_id})
    
    if not chat_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    if user_id not in chat_doc["participants"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this chat"
        )
    
    # Create message
    message = Message(
        chat_id=chat_id,
        sender_id=user_id,
        text=message_data.text,
        message_type=message_data.message_type
    )
    
    message_dict = message.dict()
    message_dict["_id"] = message_dict.pop("id")
    
    # Insert message
    result = await db.messages.insert_one(message_dict)
    
    if result.inserted_id:
        # Update chat's last message
        last_message = LastMessage(
            text=message.text,
            sender_id=message.sender_id,
            timestamp=message.timestamp,
            status=message.status
        )
        
        await db.chats.update_one(
            {"_id": chat_id},
            {"$set": {
                "last_message": last_message.dict(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        return MessageResponse(
            id=message.id,
            chat_id=message.chat_id,
            sender_id=message.sender_id,
            text=message.text,
            timestamp=message.timestamp,
            status=message.status,
            message_type=message.message_type,
            created_at=message.created_at
        )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to send message"
    )

@router.put("/messages/{message_id}/status", response_model=MessageResponse)
async def update_message_status(
    message_id: str,
    status_data: MessageStatusUpdate,
    user_id: str = Depends(auth_handler.auth_wrapper)
):
    """Update message status (delivered/read)"""
    
    # Get message
    message_doc = await db.messages.find_one({"_id": message_id})
    
    if not message_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Verify user has access to the chat
    chat_doc = await db.chats.find_one({"_id": message_doc["chat_id"]})
    
    if not chat_doc or user_id not in chat_doc["participants"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this message"
        )
    
    # Only allow certain status transitions
    valid_statuses = ["sent", "delivered", "read"]
    if status_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid message status"
        )
    
    # Update message status
    result = await db.messages.update_one(
        {"_id": message_id},
        {"$set": {
            "status": status_data.status,
            "updated_at": datetime.utcnow()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update message status"
        )
    
    # Update chat's last message status if this is the latest message
    if message_doc["_id"] == chat_doc.get("last_message", {}).get("_id"):
        await db.chats.update_one(
            {"_id": message_doc["chat_id"]},
            {"$set": {
                "last_message.status": status_data.status,
                "updated_at": datetime.utcnow()
            }}
        )
    
    # Get updated message
    updated_message_doc = await db.messages.find_one({"_id": message_id})
    
    return MessageResponse(
        id=updated_message_doc["_id"],
        chat_id=updated_message_doc["chat_id"],
        sender_id=updated_message_doc["sender_id"],
        text=updated_message_doc["text"],
        timestamp=updated_message_doc["timestamp"],
        status=updated_message_doc["status"],
        message_type=updated_message_doc["message_type"],
        created_at=updated_message_doc["created_at"]
    )

@router.get("/messages/unread-count")
async def get_unread_count(user_id: str = Depends(auth_handler.auth_wrapper)):
    """Get total unread message count for user"""
    
    # Get all chats where user is participant
    chats_cursor = db.chats.find({"participants": user_id})
    chats = await chats_cursor.to_list(1000)
    
    total_unread = 0
    
    for chat in chats:
        # Count unread messages in each chat
        unread_count = await db.messages.count_documents({
            "chat_id": chat["_id"],
            "sender_id": {"$ne": user_id},  # Messages not sent by current user
            "status": {"$in": ["sent", "delivered"]}  # Not read yet
        })
        
        total_unread += unread_count
    
    return {"unread_count": total_unread}