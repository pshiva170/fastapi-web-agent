import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

load_dotenv()

API_SECRET_KEY = os.getenv("API_SECRET_KEY")
if not API_SECRET_KEY:
    raise ValueError("API_SECRET_KEY environment variable not set!")

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if not api_key or not api_key.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header",
        )
    
    token = api_key.split(" ")[1]
    
    if token == API_SECRET_KEY:
        return token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
