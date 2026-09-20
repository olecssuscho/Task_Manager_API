from fastapi import APIRouter, Depends
from schemas.models import TaskMODELS,UserMODELS,TaskFromTextRequest
from schemas.responces import TaskRESPONCES
from fastapi_pagination import Page
from depends import get_current_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.tasks import (
    create_tasks_services,
    get_all_tasks_services,
    update_task_services,
    delete_task_services,
    create_from_text_services,
    get_task_from_text)


router = APIRouter(prefix="/task",tags=["Tasks"])

@router.post("/create",response_model=TaskRESPONCES)
async def create_tasks(task:TaskMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await create_tasks_services(task,task.assignee_email,user,db)

@router.get("/{id}/tasks",response_model=Page[TaskRESPONCES])
async def get_all_tasks(id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await get_all_tasks_services(id,user,db)

@router.put("/{id}")
async def update_task(id:int,task:TaskMODELS,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await update_task_services(id,task,task.assignee_email,user,db)

@router.delete("/{id}")
async def delete_task(id:int,user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await delete_task_services(id,user,db)

@router.post("/create-from-text")
async def create_from_text(body:TaskFromTextRequest, user:UserMODELS = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    return await create_from_text_services(body.text,body.project_id,body.assignee_email,user,db)

@router.get("/search/{project_id}",response_model=list[TaskRESPONCES])
async def get_from_text(text:str, project_id:int, user:UserMODELS = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    return await get_task_from_text(text,project_id,user,db)