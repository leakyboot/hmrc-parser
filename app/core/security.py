from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate test user passwords
def get_test_users() -> Dict[str, Dict[str, str]]:
    """Generate test user configuration with proper password hashes."""
    password = "testpass"
    hashed_password = pwd_context.hash(password)
    return {
        "testuser": {
            "username": "testuser",
            "hashed_password": hashed_password,
            "role": "user"
        },
        "admin": {
            "username": "admin",
            "hashed_password": hashed_password,
            "role": "admin"
        },
        "readonly": {
            "username": "readonly",
            "hashed_password": hashed_password,
            "role": "readonly"
        }
    }

# Test environment configuration
TEST_USERS = get_test_users()

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

class SecurityManager:
    @staticmethod
    def verify_credentials(username: str, password: str) -> bool:
        """Verify user credentials."""
        try:
            if username not in TEST_USERS:
                return False
            user = TEST_USERS[username]
            return SecurityManager.verify_password(password, user["hashed_password"])
        except Exception as e:
            print(f"Error verifying credentials: {str(e)}")
            return False

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            print(f"Error verifying password: {str(e)}")
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def verify_token(token: str) -> dict:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

class RBACManager:
    """Role-Based Access Control Manager"""
    
    ROLES = {
        "admin": ["upload", "read", "delete", "manage_users"],
        "user": ["upload", "read", "delete_own"],
        "readonly": ["read"]
    }

    @staticmethod
    def check_permission(user_role: str, required_permission: str) -> bool:
        """Check if user role has the required permission."""
        if user_role not in RBACManager.ROLES:
            return False
        return required_permission in RBACManager.ROLES[user_role]

    @staticmethod
    async def verify_permission(token: str, required_permission: str) -> bool:
        """Verify if the token has the required permission."""
        try:
            payload = await SecurityManager.verify_token(token)
            user_role = payload.get("role", "readonly")
            return RBACManager.check_permission(user_role, required_permission)
        except HTTPException:
            return False
