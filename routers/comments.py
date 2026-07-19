from fastapi import APIRouter, Depends
from schemas.models import UserMODELS,CommentMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.comments import create_comment_services,get_comment_services,delete_comment_services

router = APIRouter(prefix="/comment", tags=["Comments"])

@router.post("/task/{id}/comment")
async def create_comment(task_id:int,comment:CommentMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await create_comment_services(task_id,comment,user,db)

@router.get("/task/{id}/comments")
async def get_comment(task_id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await get_comment_services(task_id,user,db)

@router.delete("/{id}")
async def delete_comment(id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await delete_comment_services(id,user,db)