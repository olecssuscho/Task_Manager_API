from sqlalchemy import select,delete
from fastapi import HTTPException,status
from fastapi_pagination.ext.sqlalchemy import paginate
from schemas.dbmodels import UserDB,CommentDB,TaskDB
from sqlalchemy.ext.asyncio import AsyncSession
from depends import get_role
from websocket import manager
import logging

logger = logging.getLogger(__name__)

async def create_comment_services(task_id:int,comment:CommentDB,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == task_id))
    task = stmt.scalar_one_or_none()
    if not task:
        logger.warning(f"User: {user.id} tried to create comment to task: {task_id}, but task was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    await get_role(task.project_id,"editor",user,db)

    project_id = task.project_id
    user_id = user.id
    task_id_real = task.id
    comm = CommentDB(text = comment.text, task_id = task_id, user_id = user.id)
    db.add(comm)
    await db.commit()
    await db.refresh(comm)
    comm_id = comm.id
    logger.info(f"User: {user_id} created comment: {comm_id} to task: {task_id_real}")
    await manager.broadcast(project_id,"Comment created")
    return comm

async def get_comments_services(task_id:int,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == task_id))
    task = stmt.scalar_one_or_none()
    if not task:
        logger.warning(f"User: {user.id} tried to get all comments to task: {task_id}, but task was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    await get_role(task.project_id,"viewer",user,db)
    comm = (select(CommentDB).filter(CommentDB.task_id == task_id))
    logger.info(f"User: {user.id} get all comments related to task: {task.id}")
    return await paginate(db,comm)
    
async def delete_comment_services(id:int,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(CommentDB).filter(CommentDB.id == id))
    comm = stmt.scalar_one_or_none()
    if not comm:
        logger.warning(f"User: {user.id} tried to delete comment: {id}, but comment was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment did not found")
    task_test = await db.execute(select(TaskDB).filter(TaskDB.id == comm.task_id))
    task = task_test.scalar_one_or_none()
    task_id = task.id
    project_id = task.project_id
    comm_id = comm.id
    user_id = user.id
    await get_role(task.project_id,"editor",user,db)
    await db.execute(delete(CommentDB).filter(CommentDB.id == id))
    await db.commit()
    logger.info(f"User: {user_id} delete comment: {comm_id} related to task: {task_id}")
    await manager.broadcast(project_id,"Comment deleted")
    return "Success"
