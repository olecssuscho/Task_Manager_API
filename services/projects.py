from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import select,update,delete
from schemas.dbmodels import ProjectDB,UserDB,ProjectMemberDB
from depends import get_role
import logging

logger = logging.getLogger(__name__)

async def create_project_services(project:ProjectDB,user:UserDB,db:AsyncSession):
    owner_id = user.id
    project_db = ProjectDB(
        name = project.name,
        description = project.description,
        owner_id = owner_id
    )
    user_id = user.id
    db.add(project_db)
    await db.commit()
    await db.refresh(project_db)
    project_member_db = ProjectMemberDB(project_id=project_db.id, user_id=owner_id, role="owner")
    db.add(project_member_db)
    await db.commit()
    await db.refresh(project_db)
    logger.info(f"User: {user_id} create new project: {project_db.id}")
    return project_db

async def get_project_services(user:UserDB,db:AsyncSession):
    projects = (select(ProjectDB).filter(ProjectMemberDB.user_id == user.id, ProjectMemberDB.project_id == ProjectDB.id))
    logger.info(f"User: {user.id} get all projects")
    return await apaginate(db,projects)

async def get_project_id_services(id:int,user:UserDB,db:AsyncSession):
    await get_role(id,"viewer",user,db)
    stmt = await db.execute(select(ProjectMemberDB).filter((ProjectMemberDB.user_id == user.id),(ProjectMemberDB.project_id ==id)))
    result = stmt.scalar_one_or_none()
    if not result:
        logger.warning(f"User {user.id}, tried to get particular project: {id}, but project was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")
    logger.info(f"User: {user.id} get particulat project: {result.project_id}")
    return result

async def update_project_services(id:int,project:ProjectDB,user:UserDB,db:AsyncSession):
    await get_role(id,"owner",user,db)
    result = await db.execute(select(ProjectDB).filter(ProjectDB.id == id))
    prod = result.scalar_one_or_none()
    if not prod:
        logger.warning(f"User {user.id}, tried to update project: {id}, but project was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")
    
    if prod.owner_id != user.id:
        logger.warning(f"User {user.id}, tried to update project: {id}, but he was not owner")
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="You are not owner")
   
    await db.execute(update(ProjectDB).filter(ProjectDB.id == id).values(name = project.name,description = project.description))
    user_id = user.id
    project_id = prod.id
    await db.commit()
    logger.info(f"User: {user_id} get particulat project: {project_id}")
    return "Success"
    
async def delete_project_services(id:int,user:UserDB,db:AsyncSession):
    await get_role(id,"owner",user,db)
    result = await db.execute(select(ProjectDB).filter(ProjectDB.id == id))
    prod = result.scalar_one_or_none()
    if not prod:
        logger.warning(f"User {user.id}, tried to update project: {id}, but project was not exist")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")
    
    if prod.owner_id != user.id:
        logger.warning(f"User {user.id}, tried to update project: {id}, but he was not owner")
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="You are not owner")
   
    await db.execute(delete(ProjectDB).filter(ProjectDB.id ==id))
    user_id = user.id
    project_id = prod.id
    await db.commit()
    logger.info(f"User: {user_id} delete particulat project: {project_id}")
    return "Success"