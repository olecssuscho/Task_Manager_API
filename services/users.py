from sqlalchemy.ext.asyncio import AsyncSession
from schemas.dbmodels import UserDB
from auth import create_refresh_token,hash_password

async def register_services(user:UserDB,db:AsyncSession):
    refresh_token = create_refresh_token({"email":user.email})
    password = user.password
    hashed_password = hash_password(password)
    user.password = hashed_password
    db.add(UserDB(**user.model_dump(),refresh_token = refresh_token))
    await db.commit()
    return refresh_token