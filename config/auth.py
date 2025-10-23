"""
Bearer token authentication using FastAPI security dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

security = HTTPBearer(auto_error=False)

def get_bearer_token() -> str:
    """Get the expected bearer token from environment variables"""
    auth_enabled = os.getenv("USE_AUTH", "false").lower() == "true"
    if not auth_enabled:
        return None

    bearer_token = os.getenv("BEARER_TOKEN", "")
    if not bearer_token:
        raise ValueError(
            "ENABLE_AUTH is set to true but BEARER_TOKEN environment variable is not set. "
            "Please configure BEARER_TOKEN in your .env file."
        )
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
