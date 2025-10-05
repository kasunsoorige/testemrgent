from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from models.user import UserResponse
from auth.auth_handler import auth_handler
from database import db
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    user_id: str = Depends(auth_handler.auth_wrapper),
    search: Optional[str] = Query(None, description="Search users by name, email, or phone"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all users (for contacts/search)"""
    
    # Build query
    query = {"_id": {"$ne": user_id}}  # Exclude current user
    
    if search:
        # Search by name, email, or phone
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}}
        ]
    
    # Get users with pagination
    users_cursor = db.users.find(query).limit(limit).skip(offset)
    users = await users_cursor.to_list(limit)
    
    # Convert to response format
    user_responses = []
    for user_doc in users:
        user_responses.append(UserResponse(
            id=user_doc["_id"],
            name=user_doc["name"],
            email=user_doc.get("email"),
            phone=user_doc.get("phone"),
            avatar=user_doc.get("avatar"),
            status=user_doc["status"],
            is_online=user_doc["is_online"],
            last_seen=user_doc["last_seen"],
            created_at=user_doc["created_at"]
        ))
    
    return user_responses

@router.get("/{target_user_id}", response_model=UserResponse)
async def get_user_by_id(
    target_user_id: str,
    user_id: str = Depends(auth_handler.auth_wrapper)
):
    """Get specific user by ID"""
    
    user_doc = await db.users.find_one({"_id": target_user_id})
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user_doc["_id"],
        name=user_doc["name"],
        email=user_doc.get("email"),
        phone=user_doc.get("phone"),
        avatar=user_doc.get("avatar"),
        status=user_doc["status"],
        is_online=user_doc["is_online"],
        last_seen=user_doc["last_seen"],
        created_at=user_doc["created_at"]
    )

@router.put("/{target_user_id}/status")
async def update_user_status(
    target_user_id: str,
    is_online: bool,
    user_id: str = Depends(auth_handler.auth_wrapper)
):
    """Update user online status (admin only or self)"""
    
    # Only allow users to update their own status
    if user_id != target_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own status"
        )
    
    update_data = {
        "is_online": is_online,
        "updated_at": datetime.utcnow()
    }
    
    if not is_online:
        update_data["last_seen"] = datetime.utcnow()
    
    result = await db.users.update_one(
        {"_id": target_user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": f"User status updated to {'online' if is_online else 'offline'}"}

@router.get("/search/contacts", response_model=List[UserResponse])
async def search_contacts(
    q: str = Query(..., description="Search query"),
    user_id: str = Depends(auth_handler.auth_wrapper),
    limit: int = Query(20, ge=1, le=50)
):
    """Search users for adding to contacts/starting chats"""
    
    # Get users that match search and have existing chats with current user
    chats_cursor = db.chats.find({"participants": user_id})
    chats = await chats_cursor.to_list(1000)
    
    # Get all users current user has chatted with
    existing_contact_ids = set()
    for chat in chats:
        for participant_id in chat["participants"]:
            if participant_id != user_id:
                existing_contact_ids.add(participant_id)
    
    # Search all users
    query = {
        "_id": {"$ne": user_id},
        "$or": [
            {"name": {"$regex": q, "$options": "i"}},
            {"email": {"$regex": q, "$options": "i"}},
            {"phone": {"$regex": q, "$options": "i"}}
        ]
    }
    
    users_cursor = db.users.find(query).limit(limit)
    users = await users_cursor.to_list(limit)
    
    # Convert to response format and mark existing contacts
    user_responses = []
    for user_doc in users:
        user_response = UserResponse(
            id=user_doc["_id"],
            name=user_doc["name"],
            email=user_doc.get("email"),
            phone=user_doc.get("phone"),
            avatar=user_doc.get("avatar"),
            status=user_doc["status"],
            is_online=user_doc["is_online"],
            last_seen=user_doc["last_seen"],
            created_at=user_doc["created_at"]
        )
        
        user_responses.append(user_response)
    
    # Sort: existing contacts first, then by name
    user_responses.sort(key=lambda u: (
        u.id not in existing_contact_ids,  # Existing contacts first
        u.name.lower()  # Then alphabetically
    ))
    
    return user_responses