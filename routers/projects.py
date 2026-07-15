from fastapi import APIRouter, Depends
from schemas.models import ProjectMODELS,UserMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.projects import create_project_services

router = APIRouter(prefix="/project",tags=["Projects"])

@router.post("/register")
async def create_project(project:ProjectMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    result = await create_project_services(project,user,db)
    return result