from fastapi import APIRouter, Depends
from schemas.models import UserMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.project_members import add_member_services

router = APIRouter(prefix="/project_member",tags=["Project_members"])

@router.post("/register")
async def add_member(project_id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await add_member_services(project_id,user,db)