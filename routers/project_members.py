from fastapi import APIRouter, Depends
from schemas.models import UserMODELS,ProjectMemberUpdateMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.project_members import add_member_id_services,delete_member_services,patch_member_services

router = APIRouter(prefix="/project_member",tags=["Project_members"])

@router.post("/project/{id}/member/{user_email}")
async def add_member(id:int,user_email:str,role:ProjectMemberUpdateMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await add_member_id_services(id,user_email,role,user,db)

@router.delete("/project/{id}/member/{user_email}")
async def delete_member(id:int,user_email:str,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await delete_member_services(id,user_email,user,db)

@router.patch("/project/{id}/member/{user_email}")
async def patch_member(id:int,user_email:str,role:ProjectMemberUpdateMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await patch_member_services(id,user_email,role,user,db)
