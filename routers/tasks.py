from fastapi import APIRouter, Depends
from schemas.models import TaskMODELS,UserMODELS
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.tasks import create_tasks_services

router = APIRouter(prefix="/task",tags=["Tasks"])

@router.post("/create")
async def create_tasks(task:TaskMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await create_tasks_services(task,task.assignee_email,user,db)
