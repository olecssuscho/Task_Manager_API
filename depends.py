from fastapi import Depends, HTTPException,status
from auth import decode_token
from database import Async_Session_Local
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.dbmodels import UserDB,ProjectMemberDB
import logging

logger = logging.getLogger(__name__)

user_schema = OAuth2PasswordBearer(tokenUrl="/user/login")

async def get_db():
    async with Async_Session_Local() as db:
        yield db

async def get_current_user(token:str = Depends(user_schema),db:AsyncSession = Depends(get_db)):
    payload = decode_token(token)
    if not payload or "email" not in payload:
        logger.warning("Authentication failed: invalid or malformed token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if payload.get("type")!="access":
        logger.warning(f"Authentication failed: wrong token type for email {payload.get('email')}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    else:
        result = await db.execute(select(UserDB).filter(UserDB.email == payload["email"]))
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"Authentication failed: no user found for email {payload['email']}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User with that credentials no found")
        return user
    
async def get_role(project_id:int,min_role:str,user:UserDB,db:AsyncSession):
    ROLE = {"viewer":1,"editor":2,"owner":3}
    stmt = await db.execute(select(ProjectMemberDB).filter(ProjectMemberDB.project_id == project_id, ProjectMemberDB.user_id == user.id))
    allow = stmt.scalar_one_or_none()
    if not allow:
        logger.warning(f"User: {user.id} tried to work with project: {project_id}, but he is not his member")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a project member")
    if ROLE[allow.role]<ROLE[min_role]:
        logger.warning(f"User: {user.id} tried to work with project: {project_id}, but he is not allowed")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    logger.info(f"User: {user.id} working with project: {project_id}")
    return allow
