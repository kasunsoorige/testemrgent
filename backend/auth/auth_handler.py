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
        if len(password.encode('utf-8')) > 72:
            # Pre-hash with SHA256 and base64 encode
            password_hash = hashlib.sha256(password.encode('utf-8')).digest()
            password = base64.b64encode(password_hash).decode('ascii')
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        # Apply same pre-hashing as in hash_password
        if len(plain_password.encode('utf-8')) > 72:
            # Pre-hash with SHA256 and base64 encode
            password_hash = hashlib.sha256(plain_password.encode('utf-8')).digest()
            plain_password = base64.b64encode(password_hash).decode('ascii')
        return pwd_context.verify(plain_password, hashed_password)
    
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