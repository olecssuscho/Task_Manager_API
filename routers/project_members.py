from fastapi import APIRouter, Depends
from schemas.models import UserMODELS,ProjectMemberUpdateMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.project_members import add_member_services,delete_member_services,patch_member_services

router = APIRouter(prefix="/project_member",tags=["Project_members"])

@router.post("/project/{id}/member")
async def add_member(id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await add_member_services(id,user,db)

@router.delete("/project/{id}/member/{user_id}")
async def delete_member(project_id:int,User_id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await delete_member_services(project_id,User_id,user,db)

@router.patch("/{id}/member/{user_id}")
async def patch_member(project_id:int,user_id:int,role:ProjectMemberUpdateMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await patch_member_services(project_id,user_id,role,user,db)
