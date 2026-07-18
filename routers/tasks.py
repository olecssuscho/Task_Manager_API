from fastapi import APIRouter, Depends
from schemas.models import TaskMODELS,UserMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.tasks import (
    create_tasks_services,
    get_all_tasks_services,
    update_task_services,
    delete_task_services)

router = APIRouter(prefix="/task",tags=["Tasks"])

@router.post("/create")
async def create_tasks(task:TaskMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await create_tasks_services(task,task.assignee_email,user,db)

@router.get("/{id}/tasks")
async def get_all_tasks(id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await get_all_tasks_services(id,user,db)

@router.put("/{id}")
async def update_task(id:int,task:TaskMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await update_task_services(id,task,user,db)

@router.delete("/{id}")
async def delete_task(id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await delete_task_services(id,user,db)