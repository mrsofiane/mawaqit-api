"""
Bearer token authentication using FastAPI security dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config.settings import settings
security = HTTPBearer(auto_error=False)

def get_bearer_token() -> str:
    """Get the expected bearer token from environment variables"""
    auth_enabled = settings.ENABLE_AUTH
    if not auth_enabled:
        return None

    bearer_token = settings.BEARER_TOKEN
    return bearer_token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify bearer token from Authorization header."""
    expected_token = get_bearer_token()

    if expected_token is None:
        return None

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials
