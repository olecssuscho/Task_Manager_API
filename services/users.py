from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.dbmodels import UserDB
from fastapi.security import OAuth2PasswordRequestForm
from auth import check_password, create_access_token, create_refresh_token, decode_token,hash_password

async def register_services(user:UserDB,db:AsyncSession):
    refresh_token = create_refresh_token({"email":user.email})
    password = user.password
    hashed_password = hash_password(password)
    user.password = hashed_password
    db.add(UserDB(**user.model_dump(),refresh_token = refresh_token))
    await db.commit()
    return refresh_token

async def login_services(form_data:OAuth2PasswordRequestForm,db:AsyncSession):
    result = await db.execute(select(UserDB).filter(UserDB.email==form_data.username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not check_password(form_data.password,user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password is not correct")
    access_token = create_access_token({"email": user.email})
    return {"access_token": access_token, "refresh_token": user.refresh_token,"token_type": "bearer"}

async def get_services(user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(UserDB).filter(UserDB.id == user.id))
    user = stmt.scalar_one_or_none()
    return user

async def refresh_services(user:UserDB,db:AsyncSession):
    refresh = decode_token(user.refresh_token)
    if not refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    if not "email" in refresh:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")
    if refresh.get("type")!="refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    stmt = await db.execute(select(UserDB).filter(UserDB.email == refresh["email"]))
    user = stmt.scalar_one_or_none
    if user:
        access = create_access_token({"email": refresh["email"]})
        return {"access_token": access, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")