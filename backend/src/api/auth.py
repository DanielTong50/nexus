"""Simple authentication routes for Nexus.

Provides basic email/password authentication with JWT tokens.
Users are stored in MongoDB.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt

from config.settings import settings
from src.services.database import db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.google_api_key[:32] if settings.google_api_key else "nexus-secret-key-change-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# Security
security = HTTPBearer(auto_error=False)


# Request/Response models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime


# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """Get current user from JWT token. Returns None if not authenticated."""
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        # Get user from database
        collection = db_service.db["users"]
        user = await collection.find_one({"_id": user_id})
        if user:
            return {
                "id": str(user["_id"]),
                "email": user["email"],
                "name": user.get("name"),
            }
        return None
    except JWTError:
        return None


async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Require authentication. Raises 401 if not authenticated."""
    user = await get_current_user(credentials)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# Routes
@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user."""
    collection = db_service.db["users"]

    # Check if user already exists
    existing = await collection.find_one({"email": user_data.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    import uuid
    user_id = str(uuid.uuid4())
    user_doc = {
        "_id": user_id,
        "email": user_data.email.lower(),
        "password_hash": get_password_hash(user_data.password),
        "name": user_data.name,
        "created_at": datetime.utcnow(),
    }

    await collection.insert_one(user_doc)

    # Generate token
    access_token = create_access_token(data={"sub": user_id})

    return Token(
        access_token=access_token,
        user={
            "id": user_id,
            "email": user_data.email.lower(),
            "name": user_data.name,
        }
    )


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login with email and password."""
    collection = db_service.db["users"]

    # Find user
    user = await collection.find_one({"email": login_data.email.lower()})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    if not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate token
    access_token = create_access_token(data={"sub": user["_id"]})

    return Token(
        access_token=access_token,
        user={
            "id": str(user["_id"]),
            "email": user["email"],
            "name": user.get("name"),
        }
    )


@router.get("/me")
async def get_me(user: dict = Depends(require_auth)):
    """Get current user info."""
    return user


@router.post("/logout")
async def logout():
    """Logout (client should discard token)."""
    return {"message": "Logged out successfully"}
