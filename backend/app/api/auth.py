from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import Optional
import httpx

from app.core.config import get_settings

router = APIRouter()
security = HTTPBearer(auto_error=False)
settings = get_settings()

class TokenData(BaseModel):
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    roles: list[str] = []
    aud: Optional[str] = None


class UserInfo(BaseModel):
    pass


@router.get("/auth/me", response_model=UserInfo)
async def get_current_user():
    """Get current authenticated user info.
    
    Returns 401 if not authenticated.
    """
    raise HTTPException(status_code=401, detail="Authentication required")


@router.get("/auth/login")
async def get_login_url():
    """Get login URL for OIDC authentication.
    
    Returns demo login URL for demo mode.
    """
    return {"url": "/demo-login"}
