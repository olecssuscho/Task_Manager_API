from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm,HTTPBearer,HTTPAuthorizationCredentials
from schemas.models import ChangePasswordSchema, UserMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.users import (
    register_services,
    login_services,
    get_services,
    refresh_services,
    logout_services,
    logout_all_services,
    change_password_services)
from lim import limiter

router = APIRouter(prefix="/user",tags=["Users"])

bearer = HTTPBearer()

def get_token(token:HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    return token.credentials

@router.post("/register")
@limiter.limit("5/minute")
async def register(request:Request,user:UserMODELS,db:AsyncSession = Depends(get_db)):
    return await register_services(user,db)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request:Request,form_data:OAuth2PasswordRequestForm = Depends(),db:AsyncSession = Depends(get_db)):
    return await login_services(form_data,db)

@router.get("/me")
async def get_me(user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await get_services(user,db)

@router.post("/refresh")
async def refresh(token:str = Depends(get_token),db:AsyncSession = Depends(get_db)):
    return await refresh_services(token,db)

@router.post("/logout")
async def logout(token:str = Depends(get_token),db:AsyncSession = Depends(get_db)):
    return await logout_services(token,db)

@router.post("/logout_all")
async def logout_all(user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await logout_all_services(user,db)

@router.put("/change_password")
async def change_password(data:ChangePasswordSchema,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await change_password_services(data.old_password,data.new_password,user,db)