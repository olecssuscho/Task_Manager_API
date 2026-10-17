from datetime import timedelta,datetime,timezone
from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from schemas.dbmodels import UserDB,RefreshDB
from fastapi.security import OAuth2PasswordRequestForm
from auth import check_password, create_access_token, create_refresh_token, decode_token,hash_password
from auth import hash_token,create_abs_edge
import uuid
import logging
from config import settings

logger = logging.getLogger(__name__)

async def revoke_family(family_id:RefreshDB,db:AsyncSession,reason: str = "repeat use") -> None:
    now = datetime.now(timezone.utc)
    await db.execute(update(RefreshDB).filter(RefreshDB.family_id == family_id,
                                RefreshDB.revoked_at.is_(None)).
                                values(revoked_at = now,  revoke_reason = reason))
    await db.commit()
   
async def register_services(user:UserDB,db:AsyncSession) -> str:
    stmt = await db.execute(select(UserDB).filter(UserDB.email == user.email))
    user_db = stmt.scalar_one_or_none()
    if user_db:
        logger.warning(f"Someone have tried to register with {user.email}, but it was used")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email was used")  
    
    refresh_token = create_refresh_token({"email":user.email})
    expiered = datetime.fromtimestamp(decode_token(refresh_token).get("exp"),tz=timezone.utc)
    record = hash_token(refresh_token)
    password = user.password
    
    hashed_password = hash_password(password)
    user.password = hashed_password
    user_db = UserDB(**user.model_dump(),refresh_token = record)
    db.add(user_db)
    await db.commit()
    await db.refresh(user_db)
    
    user_id = user_db.id   
    refr = RefreshDB(user_id = user_id,token_hash = record,exp = expiered,
                     family_id = uuid.uuid4(),abs_edge = create_abs_edge()) 
    
    db.add(refr)
    await db.commit()
    await db.refresh(refr)
    logger.info(f"User: {user_id} was register")
    return refresh_token

async def login_services(form_data:OAuth2PasswordRequestForm,db:AsyncSession) -> dict:
    result = await db.execute(select(UserDB).filter(UserDB.email==form_data.username))
    user = result.scalar_one_or_none()
    if not user:
        logger.warning(f"User: {form_data.username} tried to login, but he was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not check_password(form_data.password,user.password):
        logger.warning(f"User: {user.id} tried to login, but password was uncorrect")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is not correct")
    
    family_id = uuid.uuid4()
    token = create_refresh_token({"email": user.email})
    expiered = datetime.fromtimestamp(decode_token(token).get("exp"),tz=timezone.utc)
    record = hash_token(token)
    access_token = create_access_token({"email": user.email})

    refr = RefreshDB(user_id = user.id,token_hash = record,exp = expiered + timedelta(settings.ABS_DAY_LIFE),
                    family_id = family_id,abs_edge = create_abs_edge()) 
    db.add(refr)
    await db.commit()
    await db.refresh(refr)

    logger.info(f"User: {form_data.client_id} was login")
    return {"access_token": access_token, "refresh_token": token,"token_type": "bearer"}

async def get_services(user:UserDB,db:AsyncSession) -> UserDB:
    stmt = await db.execute(select(UserDB).filter(UserDB.id == user.id))
    user = stmt.scalar_one_or_none()
    return user

async def refresh_services(token:str,db:AsyncSession) -> dict:
    token_json = decode_token(token)
    if not token_json or token_json.get("type") != "refresh":
        logger.warning("Refresh failed: token not decoded or wrong type")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    test_token = hash_token(token)
    stmt = await db.execute(select(RefreshDB).filter(RefreshDB.token_hash == test_token))
    record = stmt.scalar_one_or_none()

    if not record:
        logger.warning("User tried to refresh token but token was not exist")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

    user_id = record.user_id
    now = datetime.now(timezone.utc)

    user_test = await db.execute(select(UserDB).filter(UserDB.id == user_id))
    user = user_test.scalar_one_or_none()
    if user is None:
        logger.warning(f"Refresh failed: user {user_id} not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if record.used is not None:
        logger.warning(f"User {user_id} tried to refresh token but it was used")
        await revoke_family(record.family_id,db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    
    if record.revoked_at:
        logger.warning(f"User {user_id} tried to refresh token but token was revoked")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")    
    
    if record.exp <= now:
        logger.warning(f"User {user_id} tried to refresh token but it time was expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

    if record.abs_edge <= now:
        logger.warning(f"User {user_id} tried to refresh token but abs_edge was crossed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

    res = await db.execute(update(RefreshDB).filter(RefreshDB.id == record.id,RefreshDB.used.is_(None),
                    RefreshDB.revoked_at.is_(None)).values(used = now))
    
    if res.rowcount == 0:
        logger.warning(f"Refresh token race/reuse for user {record.user_id}")
        await revoke_family(record,db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")    

    new_exp = min(record.abs_edge,now + timedelta(days=settings.REFRESH_TOKEN_TIME_DAYS))
    refresh_token = create_refresh_token({"email": user.email},new_exp)
    db.add(RefreshDB(user_id = user_id,token_hash = hash_token(refresh_token),exp = new_exp,
                     family_id = record.family_id,abs_edge = record.abs_edge))
    access_token = create_access_token({"email": user.email})
    await db.commit()

    logger.info(f"User's: {user_id} token was refreshed: {refresh_token}")
    return {"access_token": access_token, "refresh_token": refresh_token,"token_type": "bearer"}

async def logout_services(token:str,db:AsyncSession):   
    test_token = hash_token(token)
    stmt = await db.execute(select(RefreshDB).filter(RefreshDB.token_hash == test_token))
    record = stmt.scalar_one_or_none()
    if not record:
        logger.warning("User tried to logout token but record was not exist")
        return {"detail" : "successful"}

    await revoke_family(record.family_id,db,"Exit")
    return {"detail" : "successful"}