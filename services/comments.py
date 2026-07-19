from sqlalchemy import select,delete,update
from fastapi import HTTPException,status
from schemas.dbmodels import UserDB,CommentDB,TaskDB
from sqlalchemy.ext.asyncio import AsyncSession

async def create_comment_services(task_id:int,comment:CommentDB,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == task_id))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    commenter = await db.execute(select(TaskDB).filter((TaskDB.created_by == user.id) | (TaskDB.assignee_id == user.id)))
    commenter_db = commenter.scalars().all
    if not commenter_db:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your task")
    else:
        comm = CommentDB(text = comment.text, task_id = task_id, user_id = user.id)
        db.add(comm)
        await db.commit()
        await db.refresh(comm)
        return comm

async def get_comment_services(task_id:int,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == task_id))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task did not found")
    else:
        comm = await db.execute(select(CommentDB).filter(CommentDB.task_id == task_id))
        res = comm.scalars().all()
        return res
    
async def delete_comment_services(id:int,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(CommentDB).filter(CommentDB.id == id))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment did not found")
    else:
        await db.execute(delete(CommentDB).filter(CommentDB.id == id))
        await db.commit()
        return "Success"
