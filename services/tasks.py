from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,delete
from schemas.dbmodels import TaskDB, UserDB

async def create_tasks_services(task:TaskDB,asiigne_email:str,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(UserDB).filter(UserDB.email == asiigne_email))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    task_db = TaskDB(
        title = task.title,
        description = task.description,
        status = task.status,
        priority = task.priority,
        deadline = task.deadline,
        project_id = task.project_id,
        assignee_id = result.id,
        created_by = user.id
    )
    db.add(task_db)
    await db.commit()
    await db.refresh(task_db)
    return task_db

async def get_all_tasks_services(id:int,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.project_id == id))
    result = stmt.scalars().all()
    return result

async def update_task_services(id:int,task:TaskDB,task_email:str,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == id))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    user_db = await db.execute(select(UserDB).filter(task_email == UserDB.email))
    user_id = user_db.scalar_one_or_none().id
    await db.execute(update(TaskDB).filter(TaskDB.id == id).values(
        title = task.title, description = task.description,
        status = task.status, priority = task.priority,
        deadline = task.deadline, project_id = task.project_id,
        assignee_id = user_id
    ))
    await db.commit()
    return "Success"

async def delete_task_services(id:int,user:UserDB,db:AsyncSession):
    task = await db.execute(select(TaskDB).filter(TaskDB.id == id))
    task_db = task.scalar_one_or_none()
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    User = await db.execute(select(TaskDB).filter(TaskDB.id == id,TaskDB.created_by == user.id))
    user_db = User.scalar_one_or_none()
    if not user_db:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="It is not your task")
    
    await db.execute(delete(TaskDB).filter(TaskDB.id == id,TaskDB.created_by == user.id))
    await db.commit()
    return "Success"