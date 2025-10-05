from fastapi import APIRouter, HTTPException, status, Depends
from models.user import UserCreate, UserLogin, User, UserResponse, UserUpdate
from auth.auth_handler import auth_handler
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["authentication"])

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = None
    if user_data.email:
        existing_user = await db.users.find_one({"email": user_data.email})
    if not existing_user and user_data.phone:
        existing_user = await db.users.find_one({"phone": user_data.phone})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email or phone already exists"
        )
    
    # Hash password and create user
    hashed_password = auth_handler.hash_password(user_data.password)
    
    user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        avatar=user_data.avatar,
        status=user_data.status,
        password_hash=hashed_password,
        is_online=True
    )
    
    # Insert user to database
    user_dict = user.dict()
    user_dict["_id"] = user_dict.pop("id")
    
    result = await db.users.insert_one(user_dict)
    
    if result.inserted_id:
        # Generate JWT token
        token = auth_handler.encode_token(user.id)
        
        return {
            "message": "User registered successfully",
            "token": token,
            "user": UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                phone=user.phone,
                avatar=user.avatar,
                status=user.status,
                is_online=user.is_online,
                last_seen=user.last_seen,
                created_at=user.created_at
            )
        }
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create user"
    )

@router.post("/login", response_model=dict)
async def login_user(login_data: UserLogin):
    """Login user with email/phone and password"""
    
    # Find user by email or phone
    query = {}
    if login_data.email:
        query["email"] = login_data.email
    elif login_data.phone:
        query["phone"] = login_data.phone
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone number is required"
        )
    
    user_doc = await db.users.find_one(query)
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not auth_handler.verify_password(login_data.password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Update user online status
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"is_online": True, "updated_at": datetime.utcnow()}}
    )
    
    # Generate JWT token
    token = auth_handler.encode_token(user_doc["_id"])
    
    return {
        "message": "Login successful",
        "token": token,
        "user": UserResponse(
            id=user_doc["_id"],
            name=user_doc["name"],
            email=user_doc.get("email"),
            phone=user_doc.get("phone"),
            avatar=user_doc.get("avatar"),
            status=user_doc["status"],
            is_online=True,
            last_seen=user_doc["last_seen"],
            created_at=user_doc["created_at"]
        )
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str = Depends(auth_handler.auth_wrapper)):
    """Get current user profile"""
    
    user_doc = await db.users.find_one({"_id": user_id})
    
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

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdate,
    user_id: str = Depends(auth_handler.auth_wrapper)
):
    """Update user profile"""
    
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.users.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return updated user
    user_doc = await db.users.find_one({"_id": user_id})
    
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

@router.post("/logout")
async def logout_user(user_id: str = Depends(auth_handler.auth_wrapper)):
    """Logout user (set offline)"""
    
    await db.users.update_one(
        {"_id": user_id},
        {"$set": {
            "is_online": False,
            "last_seen": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": "Logout successful"}