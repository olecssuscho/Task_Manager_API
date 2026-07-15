from fastapi import APIRouter, Depends
from schemas.models import UserMODELS
from depends import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.users import register_services

router = APIRouter(prefix="/user",tags=["Users"])

@router.post("/register")
async def register(user:UserMODELS,db:AsyncSession = Depends(get_db)):
    result = await register_services(user,db)
    return result