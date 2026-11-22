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
