from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.dbmodels import TaskDB, UserDB

async def create_tasks_services(task:TaskDB,asiigne_email:str,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(UserDB).filter(UserDB.email == asiigne_email))
    user_db = await db.execute(select(UserDB).filter(UserDB.email == user.email)) 
    task_db = TaskDB(
        title = task.title,
        description = task.description,
        status = task.status,
        priority = task.priority,
        deadline = task.deadline,
        project_id = task.project_id,
        assignee_id = stmt.scalar_one_or_none().id,
        created_by = user_db.scalar_one_or_none().id
    )
    db.add(task_db)
    await db.commit()
    await db.refresh(task_db)
    return task_db