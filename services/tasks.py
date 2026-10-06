from datetime import datetime, timezone
import logging
from fastapi import HTTPException,status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select,update,delete
from schemas.dbmodels import TaskDB,UserDB,CommentDB,ProjectDB
from depends import get_role
from schemas.models import TaskMODELS
from websocket import manager
import services.ai_client as ai_client

logger = logging.getLogger(__name__)

async def create_tasks_services(task:TaskDB,project_id:int,asiigne_email:str,user:UserDB,db:AsyncSession):
    project_test = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    project = project_test.scalar_one_or_none()
    if not project:
        logger.warning(f"User: {user.id} tried to create task related to project: {task.project_id}, but that project does not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    project_id_real = project.id
    await get_role(project_id_real,"editor",user,db)  
    stmt = await db.execute(select(UserDB).filter(UserDB.email == asiigne_email))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    emd = ai_client.generate_embedding([task.title,task.description])
    task_db = TaskDB(
        title = task.title,
        description = task.description,
        status = task.status,
        priority = task.priority,
        deadline = task.deadline,
        project_id = project_id_real,
        assignee_id = result.id,
        created_by = user.id,
        embedding = emd
    )
    user_id = user.id
    db.add(task_db)
    await db.commit()
    await db.refresh(task_db)
    logger.info(f"User: {user_id} created task: {task_db.id} to project: {task_db.project_id}")
    await manager.broadcast(task_db.project_id,"Task created")
    return task_db

async def get_all_tasks_services(id:int,user:UserDB,db:AsyncSession):
    project_test = await db.execute(select(ProjectDB).filter(ProjectDB.id == id))
    project = project_test.scalar_one_or_none()
    if not project:
        logger.warning(f"User: {user.id} tried to get task related to project: {id}, but that project does not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    project_id = project.id
    await get_role(project_id,"viewer",user,db)

    stmt = select(TaskDB).filter(TaskDB.project_id == project_id)
    logger.info(f"User: {user.id} get all tasks to project: {project_id}")
    return await paginate(db,stmt)

async def update_task_services(id:int,task:TaskDB,task_email:str,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == id))
    task_db = stmt.scalar_one_or_none()
    if not task_db:
        logger.warning(f"User: {user.id} tried to update task: {id} , but that task does not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    project_id = task_db.project_id
    await get_role(project_id,"editor",user,db)
    user_db = await db.execute(select(UserDB).filter(task_email == UserDB.email))
    assigne = user_db.scalar_one_or_none()
    if not assigne:
        logger.warning(f"User: {user.id} had tried to update task: {id} related to project: {project_id}, but email: {task_email} was not assigne to that task")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    emd = ai_client.generate_embedding([task.title,task.description])
    await db.execute(update(TaskDB).filter(TaskDB.id == id).values(
        title = task.title, description = task.description,
        status = task.status, priority = task.priority,
        deadline = task.deadline, project_id = project_id,
        assignee_id = assigne.id, embedding=emd
    ))
    user_id = user.id
    await db.commit()
    logger.info(f"User: {user_id} update task: {id} to project: {project_id}")
    await manager.broadcast(project_id,"Task updated")
    return "Success"

async def delete_task_services(id:int,user:UserDB,db:AsyncSession):
    task = await db.execute(select(TaskDB).filter(TaskDB.id == id))
    task_db = task.scalar_one_or_none()
    if not task_db:
        logger.warning(f"User: {user.id} tried to delete task: {id}, but that task does not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    task_id = task_db.id
    project_id = task_db.project_id
    user_id = user.id
    await get_role(project_id,"editor",user,db) 
    await db.execute(delete(TaskDB).filter(TaskDB.id == id))
    await db.commit()
    logger.info(f"User: {user_id} delete task: {task_id} to project: {project_id}")
    await manager.broadcast(project_id,"Task deleted")
    return "Success"

async def create_from_text_services(text:str,project_id:int,assignee_email:str,user:UserDB,db:AsyncSession):
    project_test = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    project = project_test.scalar_one_or_none()
    if not project:
        logger.warning(f"User: {user.id} tried to create task from text related to project: {project_id}, but that project does not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    
    user_db = await db.execute(select(UserDB).filter(assignee_email == UserDB.email))
    assigne = user_db.scalar_one_or_none()
    if not assigne:
        logger.warning(f"User: {user.id} had tried to create task from text related to project: {project.id}, but email: {assignee_email} was not assigne to that task")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    get_role(project.id,"editor",user,db)
    try:
        ai_data = ai_client.generate_task_data_from_text(text)
    except Exception as e:
        if "429" in str(e):
            logger.warning("Claude rate limit exceeded")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI rate limit reached, try again later")
        logger.exception("AI service call failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable")
    try:
        emd = ai_client.generate_embedding([ai_data.title,ai_data.description])
        task_input = TaskMODELS(
            title=ai_data.title,
            description=ai_data.description,
            priority=ai_data.priority,
            deadline=datetime.fromisoformat(f"{ai_data.deadline}"),
            project_id=project.id,
            status="todo",
            assignee_email = assigne.email,
            embedding = emd
        )
    except Exception as e:
        logger.warning(f"Task was not created due {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Could not parse a valid task from the text")

    return await create_tasks_services(task_input,assignee_email,user,db)

async def get_task_from_text(text:str,project_id:int,user:UserDB,db:AsyncSession):
    project_test = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    project = project_test.scalar_one_or_none()
    if not project:
        logger.warning(f"User: {user.id} tried to get task from text related to project: {project_id}, but that project does not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    
    get_role(project.id,"editor",user,db)
    try:
        vector = ai_client.generate_embedding([text])
    except Exception as e:
        if "429" in str(e):
            logger.warning("Voyage rate limit exceeded")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI rate limit reached, try again later")
        logger.exception("AI service call failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable")

    stmt = await db.execute(select(TaskDB).order_by(TaskDB.embedding.cosine_distance(vector)).limit(1))
    tasks = stmt.scalars()
    logger.info(f"User: {user.id} get info about tasks according: {text}, that was related to project: {project_id}")
    return tasks

async def suggest_services(title:str,description:str,user:UserDB,db:AsyncSession):  
    try:
        sug = ai_client.suggest([title,description])
    except Exception as e:
        if "429" in str(e):
            logger.warning("Claude rate limit exceeded")
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI rate limit reached, try again later")
        logger.exception("AI service call failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable")
    logger.info(f"User: {user.id} use suggest according to title: {title} and description: {description}")
    return {
        "title": title,
        "description":description,
        "priority": sug.priority,
        "reasoning": sug.reasoning
    }

async def sumarize_services(id:int, user:UserDB, db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == id))
    task = stmt.scalar_one_or_none()
    if not task:
        logger.warning(f"User: {user.id} tried to summarize comments on task: {id} , but that task does not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    
    get_role(task.project_id,"editor",user,db)

    tasks_test = await db.execute(select(TaskDB).join(CommentDB, task.id == CommentDB.task_id).filter(
        or_(task.summary_updated_at == None, task.summary_updated_at < CommentDB.created_at)).distinct())

    tasks = tasks_test.scalars()

    for task in tasks:
        comments_test = await db.execute(select(CommentDB.text).filter(CommentDB.task_id == task.id))
        comments = comments_test.scalars()
        comment_texts = [c.text for c in comments]
        summary = ai_client.resumes(comment_texts)
        task.comments_summary = summary
        task.summary_updated_at = datetime.now(timezone.utc)
    logger.info(f"User: {user.id} create summarize comments for task: {task.id} related to project: {task.project_id}")
    return task.comments_summary