from datetime import datetime
import logging
from fastapi import HTTPException,status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,delete
from schemas.dbmodels import TaskDB,UserDB
from depends import get_role
from schemas.models import TaskMODELS
from websocket import manager
from services.ai_client import generate_task_data_from_text, generate_embedding,suggest

logger = logging.getLogger(__name__)

async def create_tasks_services(task:TaskDB,asiigne_email:str,user:UserDB,db:AsyncSession):
    await get_role(task.project_id,"editor",user,db)  
    stmt = await db.execute(select(UserDB).filter(UserDB.email == asiigne_email))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    emd = generate_embedding(str([str(task.title)+str(task.description)]))
    task_db = TaskDB(
        title = task.title,
        description = task.description,
        status = task.status,
        priority = task.priority,
        deadline = task.deadline,
        project_id = task.project_id,
        assignee_id = result.id,
        created_by = user.id,
        embedding = emd
    )
    db.add(task_db)
    await db.commit()
    await db.refresh(task_db)
    await manager.broadcast(task_db.project_id,"Task created")
    return task_db

async def get_all_tasks_services(id:int,user:UserDB,db:AsyncSession):
    await get_role(id,"viewer",user,db)

    stmt = select(TaskDB).filter(TaskDB.project_id == id)
    return await paginate(db,stmt)

async def update_task_services(id:int,task:TaskDB,task_email:str,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == id))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    await get_role(result.project_id,"editor",user,db)
    user_db = await db.execute(select(UserDB).filter(task_email == UserDB.email))
    assigne = user_db.scalar_one_or_none()
    if not assigne:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    emd = generate_embedding(str([str(task.title)+str(task.description)]))
    await db.execute(update(TaskDB).filter(TaskDB.id == id).values(
        title = task.title, description = task.description,
        status = task.status, priority = task.priority,
        deadline = task.deadline, project_id = task.project_id,
        assignee_id = assigne.id, embedding=emd
    ))
    await db.commit()
    await manager.broadcast(task.project_id,"Task updated")
    return "Success"

async def delete_task_services(id:int,user:UserDB,db:AsyncSession):
    task = await db.execute(select(TaskDB).filter(TaskDB.id == id))
    task_db = task.scalar_one_or_none()
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    await get_role(task_db.project_id,"editor",user,db) 
    await db.execute(delete(TaskDB).filter(TaskDB.id == id))
    await db.commit()
    await manager.broadcast(task_db.project_id,"Task deleted")
    return "Success"

async def create_from_text_services(text:str,project_id:int,assignee_email:str,user:UserDB,db:AsyncSession):
    get_role(project_id,"editor",user,db)
    try:
        ai_data = generate_task_data_from_text(text)
    except Exception as e:
        if "429" in str(e):
            logger.warning("Claude rate limit exceeded")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI rate limit reached, try again later")
        logger.exception("AI service call failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable")
    try:
        emd = generate_embedding([ai_data.title,ai_data.description])
        task_input = TaskMODELS(
            title=ai_data.title,
            description=ai_data.description,
            priority=ai_data.priority,
            deadline=datetime.fromisoformat(f"{ai_data.deadline}"),
            project_id=project_id,
            status="todo",
            assignee_email = assignee_email,
            embedding = emd
        )
    except Exception:
        logger.warning(f"Task was not created: {task_input}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Could not parse a valid task from the text")

    return await create_tasks_services(task_input,assignee_email,user,db)

async def get_task_from_text(text:str,project_id:int,user:UserDB,db:AsyncSession):
    get_role(project_id,"editor",user,db)
    try:
        vector = generate_embedding(text)
    except Exception as e:
        if "429" in str(e):
            logger.warning("Voyage rate limit exceeded")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI rate limit reached, try again later")
        logger.exception("AI service call failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable")

    stmt = await db.execute(select(TaskDB).order_by(TaskDB.embedding.cosine_distance(vector)).limit(1))
    tasks = stmt.scalars()
    return tasks

async def suggest_services(title:str,description:str,user:UserDB,db:AsyncSession):
    try:
        sug = suggest([title,description])
    except Exception as e:
        if "429" in str(e):
            logger.warning("Claude rate limit exceeded")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI rate limit reached, try again later")
        logger.exception("AI service call failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable")

    return {
        "title": title,
        "description":description,
        "priority": sug.priority,
        "reasoning": sug.reasoning
    }