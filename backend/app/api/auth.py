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
    roles: list[str] = []
    aud: Optional[str] = None


class UserInfo(BaseModel):
    sub: str
    email: Optional[str] = None
    name: Optional[str] = None
    roles: list[str] = []


async def get_jwks() -> dict:
    if not settings.oidc_issuer_url:
        return {}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.oidc_issuer_url}/protocol/openid-connect/certs")
        response.raise_for_status()
        return response.json()


async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not settings.oidc_issuer_url:
        # Demo mode: accept any token
        return TokenData(sub="demo-user", email="demo@example.com", roles=["viewer", "operator"])

    try:
        jwks = await get_jwks()
        unverified_header = jwt.get_unverified_header(credentials.credentials)
        kid = unverified_header.get("kid")

        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                break

        if not key:
            raise HTTPException(status_code=401, detail="Invalid token key")

        payload = jwt.decode(
            credentials.credentials,
            key,
            algorithms=["RS256"],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer_url,
        )

        roles = payload.get("realm_access", {}).get("roles", [])
        return TokenData(
            sub=payload.get("sub", ""),
            email=payload.get("email"),
            roles=roles,
            aud=payload.get("aud"),
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


def require_role(required_roles: list[str]):
    def role_checker(token: TokenData = Depends(validate_token)) -> TokenData:
        if not any(role in token.roles for role in required_roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return token
    return role_checker


@router.get("/me", response_model=UserInfo)
async def get_current_user(token: TokenData = Depends(validate_token)):
    return UserInfo(sub=token.sub, email=token.email, roles=token.roles)


@router.get("/login")
async def login():
    if not settings.oidc_issuer_url:
        return {"url": "/demo-login"}
    auth_url = (
        f"{settings.oidc_issuer_url}/protocol/openid-connect/auth"
        f"?client_id={settings.oidc_client_id}"
        f"&redirect_uri={settings.oidc_redirect_uri}"
        f"&response_type=code"
        f"&scope=openid profile email"
        f"&state=state"
    )
    return {"url": auth_url}