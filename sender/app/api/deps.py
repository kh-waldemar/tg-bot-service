from fastapi import Header, HTTPException, status

from app.config import settings

async def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.X_API_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
