from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas.models import UserMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.users import (
    register_services,
    login_services,
    get_services,
    refresh_services)

router = APIRouter(prefix="/user",tags=["Users"])

@router.post("/register")
async def register(user:UserMODELS,db:AsyncSession = Depends(get_db)):
    result = await register_services(user,db)
    return result

@router.post("/login")
async def login(form_data:OAuth2PasswordRequestForm = Depends(),db:AsyncSession = Depends(get_db)):
    result = await login_services(form_data,db)
    return result

@router.get("/me")
async def get_me(user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await get_services(user,db)

@router.get("/refresh")
async def refresh(user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await refresh_services(user,db)