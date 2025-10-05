import jwt
from datetime import datetime, timedelta
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import hashlib
import base64

# JWT Configuration  
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "payphone-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

security = HTTPBearer()

class AuthHandler:
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with pre-hashing for long passwords"""
        # If password is longer than 72 bytes, pre-hash with SHA256
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            # Pre-hash with SHA256
            password_bytes = hashlib.sha256(password_bytes).digest()
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        # Apply same pre-hashing as in hash_password
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            # Pre-hash with SHA256
            password_bytes = hashlib.sha256(password_bytes).digest()
        
        # Verify password
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    
    def encode_token(self, user_id: str) -> str:
        """Create JWT token"""
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def decode_token(self, token: str) -> str:
        """Decode JWT token and return user_id"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired'
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )
    
    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Depends(security)):
        """FastAPI dependency for protected routes"""
        return self.decode_token(auth.credentials)

auth_handler = AuthHandler()