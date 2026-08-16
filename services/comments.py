from sqlalchemy import select,delete
from fastapi import HTTPException,status
from fastapi_pagination.ext.sqlalchemy import paginate
from schemas.dbmodels import UserDB,CommentDB,TaskDB
from sqlalchemy.ext.asyncio import AsyncSession
from depends import get_role
from websocket import manager

async def create_comment_services(task_id:int,comment:CommentDB,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == task_id))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    await get_role(result.project_id,"editor",user,db)
    commenter = await db.execute(select(TaskDB).filter((TaskDB.created_by == user.id) | (TaskDB.assignee_id == user.id)))
    commenter_db = commenter.scalars().all()
    if not commenter_db:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your task")
    else:
        comm = CommentDB(text = comment.text, task_id = task_id, user_id = user.id)
        db.add(comm)
        await db.commit()
        await db.refresh(comm)
        project = await db.execute(select(TaskDB).filter(TaskDB.id == comm.task_id))
        project_id = project.scalar_one_or_none().project_id
        await manager.broadcast(project_id,"Comment created")
        return comm

async def get_comment_services(task_id:int,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == task_id))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    await get_role(result.project_id,"viewer",user,db)
    comm = (select(CommentDB).filter(CommentDB.task_id == task_id))
    return await paginate(db,comm)
    
async def delete_comment_services(id:int,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(CommentDB).filter(CommentDB.id == id))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment did not found")
    project = await db.execute(select(TaskDB).filter(TaskDB.id == result.task_id))
    task = project.scalar_one_or_none()
    project_id = task.project_id
    await get_role(task.project_id,"editor",user,db)
    await db.execute(delete(CommentDB).filter(CommentDB.id == id))
    await db.commit()
    await manager.broadcast(project_id,"Comment deleted")
    return "Success"
