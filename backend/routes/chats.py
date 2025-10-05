from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from models.chat import ChatCreate, Chat, ChatResponse, LastMessage
from models.user import UserResponse
from auth.auth_handler import auth_handler
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

router = APIRouter(prefix="/chats", tags=["chats"])

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.get("/", response_model=List[ChatResponse])
async def get_user_chats(user_id: str = Depends(auth_handler.auth_wrapper)):
    """Get all chats for the current user"""
    
    # Find chats where user is a participant
    chats_cursor = db.chats.find({"participants": user_id})
    chats = await chats_cursor.to_list(1000)
    
    chat_responses = []
    
    for chat_doc in chats:
        # Get participant details (excluding current user)
        participant_ids = [pid for pid in chat_doc["participants"] if pid != user_id]
        
        participant_details = []
        for pid in participant_ids:
            user_doc = await db.users.find_one({"_id": pid})
            if user_doc:
                participant_details.append({
                    "id": user_doc["_id"],
                    "name": user_doc["name"],
                    "avatar": user_doc.get("avatar"),
                    "is_online": user_doc["is_online"],
                    "last_seen": user_doc["last_seen"],
                    "status": user_doc["status"]
                })
        
        # Convert to ChatResponse
        chat_response = ChatResponse(
            id=chat_doc["_id"],
            participants=chat_doc["participants"],
            type=chat_doc["type"],
            last_message=chat_doc.get("last_message"),
            is_pinned=chat_doc.get("is_pinned", False),
            created_at=chat_doc["created_at"],
            participant_details=participant_details
        )
        
        chat_responses.append(chat_response)
    
    # Sort by last message timestamp (newest first)
    chat_responses.sort(
        key=lambda x: x.last_message.timestamp if x.last_message else x.created_at,
        reverse=True
    )
    
    return chat_responses

@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    user_id: str = Depends(auth_handler.auth_wrapper)
):
    """Create a new chat"""
    
    # Ensure current user is in participants
    if user_id not in chat_data.participants:
        chat_data.participants.append(user_id)
    
    # For private chats, ensure only 2 participants
    if chat_data.type == "private" and len(chat_data.participants) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Private chats must have exactly 2 participants"
        )
    
    # Check if private chat already exists between these participants
    if chat_data.type == "private":
        existing_chat = await db.chats.find_one({
            "type": "private",
            "participants": {"$all": chat_data.participants, "$size": 2}
        })
        
        if existing_chat:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Private chat already exists between these users"
            )
    
    # Verify all participants exist
    for participant_id in chat_data.participants:
        user_exists = await db.users.find_one({"_id": participant_id})
        if not user_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {participant_id} not found"
            )
    
    # Create chat
    chat = Chat(
        participants=chat_data.participants,
        type=chat_data.type,
        is_pinned=chat_data.is_pinned
    )
    
    chat_dict = chat.dict()
    chat_dict["_id"] = chat_dict.pop("id")
    
    result = await db.chats.insert_one(chat_dict)
    
    if result.inserted_id:
        # Get participant details for response
        participant_ids = [pid for pid in chat.participants if pid != user_id]
        participant_details = []
        
        for pid in participant_ids:
            user_doc = await db.users.find_one({"_id": pid})
            if user_doc:
                participant_details.append({
                    "id": user_doc["_id"],
                    "name": user_doc["name"],
                    "avatar": user_doc.get("avatar"),
                    "is_online": user_doc["is_online"],
                    "last_seen": user_doc["last_seen"],
                    "status": user_doc["status"]
                })
        
        return ChatResponse(
            id=chat.id,
            participants=chat.participants,
            type=chat.type,
            last_message=chat.last_message,
            is_pinned=chat.is_pinned,
            created_at=chat.created_at,
            participant_details=participant_details
        )
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create chat"
    )

@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: str,
    user_id: str = Depends(auth_handler.auth_wrapper)
):
    """Get specific chat details"""
    
    chat_doc = await db.chats.find_one({"_id": chat_id})
    
    if not chat_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Check if user is participant
    if user_id not in chat_doc["participants"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this chat"
        )
    
    # Get participant details
    participant_ids = [pid for pid in chat_doc["participants"] if pid != user_id]
    participant_details = []
    
    for pid in participant_ids:
        user_doc = await db.users.find_one({"_id": pid})
        if user_doc:
            participant_details.append({
                "id": user_doc["_id"],
                "name": user_doc["name"],
                "avatar": user_doc.get("avatar"),
                "is_online": user_doc["is_online"],
                "last_seen": user_doc["last_seen"],
                "status": user_doc["status"]
            })
    
    return ChatResponse(
        id=chat_doc["_id"],
        participants=chat_doc["participants"],
        type=chat_doc["type"],
        last_message=chat_doc.get("last_message"),
        is_pinned=chat_doc.get("is_pinned", False),
        created_at=chat_doc["created_at"],
        participant_details=participant_details
    )

@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    user_id: str = Depends(auth_handler.auth_wrapper)
):
    """Delete a chat"""
    
    chat_doc = await db.chats.find_one({"_id": chat_id})
    
    if not chat_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Check if user is participant
    if user_id not in chat_doc["participants"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this chat"
        )
    
    # Delete all messages in the chat
    await db.messages.delete_many({"chat_id": chat_id})
    
    # Delete the chat
    result = await db.chats.delete_one({"_id": chat_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat"
        )
    
    return {"message": "Chat deleted successfully"}

@router.put("/{chat_id}/pin")
async def pin_chat(
    chat_id: str,
    user_id: str = Depends(auth_handler.auth_wrapper)
):
    """Pin/Unpin a chat"""
    
    chat_doc = await db.chats.find_one({"_id": chat_id})
    
    if not chat_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    # Check if user is participant
    if user_id not in chat_doc["participants"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this chat"
        )
    
    # Toggle pin status
    new_pin_status = not chat_doc.get("is_pinned", False)
    
    result = await db.chats.update_one(
        {"_id": chat_id},
        {"$set": {"is_pinned": new_pin_status, "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat"
        )
    
    return {"message": f"Chat {'pinned' if new_pin_status else 'unpinned'} successfully"}