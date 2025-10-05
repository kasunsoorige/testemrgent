import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration  
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "payphone-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

security = HTTPBearer()

class AuthHandler:
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        # Bcrypt has a 72-byte limit, so truncate if necessary
        if len(password.encode('utf-8')) > 72:
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
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