from fastapi import Depends, HTTPException,status
from auth import decode_token
from database import Async_Session_Local
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.dbmodels import UserDB

user_schema = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_db():
    async with Async_Session_Local() as db:
        yield db

async def get_current_user(token:str = Depends(user_schema),db:AsyncSession = Depends(get_db)):
    payload = decode_token(token)
    if not payload or "email" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if payload.get("type")!="access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    else:
        result = await db.execute(select(UserDB).filter(UserDB.email == payload["email"]))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User with that credentials no found")
        return user