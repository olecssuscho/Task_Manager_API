from fastapi import APIRouter, Depends
from schemas.models import ProjectMODELS,UserMODELS,ProjectUpdateMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.projects import (
    create_project_services,
    get_project_services,
    get_project_id_services,
    update_project_services,
    delete_project_services)

router = APIRouter(prefix="/project",tags=["Projects"])

@router.post("/register")
async def create_project(project:ProjectMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await create_project_services(project,user,db)

@router.get("/")
async def get_project(user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await get_project_services(user,db)

@router.get("/{id}")
async def get_project_id(id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await get_project_id_services(id,user,db)

@router.put("/{id}")
async def update_project(id:int,project:ProjectUpdateMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await update_project_services(id,project,user,db)

@router.delete("/{id}")
async def delete_project(id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await delete_project_services(id,user,db)