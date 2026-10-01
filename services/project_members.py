from sqlalchemy import select,delete,update
from fastapi import HTTPException,status
from schemas.dbmodels import ProjectDB,UserDB,ProjectMemberDB
from sqlalchemy.ext.asyncio import AsyncSession
from depends import get_role
import logging

logger = logging.getLogger(__name__)

async def add_member_id_services(project_id:int,user_email:str,role:ProjectMemberDB,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    project = stmt.scalar_one_or_none()
    if project is None:
        logger.warning(f"User: {user.id}, tried to add project member: {user_email}, to project: {project_id}, but project was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    await get_role(project.id,"owner",user,db)
    user_db = await db.execute(select(UserDB).filter(UserDB.email == user_email))
    user_real = user_db.scalar_one_or_none()
    if not user_real:
        logger.warning(f"User: {user.id}, tried to add project member: {user_email}, to project: {project_id}, but user was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    else:
        project_member_db = ProjectMemberDB(
            project_id = project.id,
            user_id = user_real.id,
            role = role.role
        )
        user_id = user.id
        new_member = user_real.id
        project_id = project.id 
        db.add(project_member_db)
        await db.commit()
        await db.refresh(project_member_db)
        logger.info(f"User: {user_id}, add new project member: {new_member} to project {project_id}")
        return project_member_db  

async def delete_member_services(project_id:int,user_email:str,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    project = stmt.scalar_one_or_none()
    if project is None:
        logger.warning(f"User: {user.id}, tried to delete project member: {user_email}, of project: {project_id}, but project was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    await get_role(project.id,"owner",user,db)
    user_not = await db.execute(select(UserDB).filter(UserDB.email == user_email))
    user_db = user_not.scalar_one_or_none()
    if user_db is None:
        logger.warning(f"User: {user.id}, tried to delete project member: {user_email}, of project: {project_id}, but user was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    user_project_member_db = await db.execute(select(ProjectMemberDB).filter(ProjectMemberDB.project_id == project.id,ProjectMemberDB.user_id == user_db.id))
    user_project_member = user_project_member_db.scalar_one_or_none()
    if user_project_member is None:
        logger.warning(f"User: {user.id}, tried to delete project member: {user_email}, of project: {project_id}, but user is not project member")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not project member")
    await db.execute(delete(ProjectMemberDB).filter(ProjectMemberDB.id == user_project_member.id))
    user_project_member_id = user_project_member.id
    project_id = project.id
    user_id = user.id
    await db.commit()
    logger.info(f"User: {user_id}, delete project member: {user_project_member_id} of project {project_id}")
    return "Success"

async def patch_member_services(project_id:int,user_email:str,role:ProjectMemberDB,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    project = stmt.scalar_one_or_none()
    if project is None:
        logger.warning(f"User: {user.id}, tried to patch project member: {user_email}, of project: {project_id}, but project was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    await get_role(project.id,"owner",user,db)
    user_test = await db.execute(select(UserDB).filter(UserDB.email == user_email))
    user_db = user_test.scalar_one_or_none()
    if user_db is None:
        logger.warning(f"User: {user.id}, tried to patch project member: {user_email}, of project: {project_id}, but user was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    user_project_member = await db.execute(select(ProjectMemberDB).filter(ProjectMemberDB.user_id == user_db.id))
    user_project_member_db = user_project_member.scalar_one_or_none()
    if user_project_member_db is None:
        logger.warning(f"User: {user.id}, tried to patch project member: {user_email}, of project: {project_id}, but user was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    await db.execute(update(ProjectMemberDB).filter(ProjectMemberDB.project_id == project_id,ProjectMemberDB.user_id == user_project_member_db.user_id).values(role = role.role))
    user_id = user.id
    user_email_db = user_db.email
    project_id_db = user_project_member_db.project_id
    logger.info(f"User: {user_id}, patch project member: {user_email_db} of project {project_id_db}")
    await db.commit()
    return "Success" 
    