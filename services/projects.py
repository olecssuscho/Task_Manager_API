from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,delete
from schemas.dbmodels import ProjectDB,UserDB,ProjectMemberDB
from depends import get_role

async def create_project_services(project:ProjectDB,user:UserDB,db:AsyncSession):
    project_db = ProjectDB(
        name = project.name,
        description = project.description,
        owner_id = user.id
    )
    db.add(project_db)
    await db.commit()
    await db.refresh(project_db)
    project_member_db = ProjectMemberDB(project_id=project_db.id, user_id=user.id, role="owner")
    await db.add(project_member_db)
    await db.commit()
    return project_db

async def get_project_services(user:UserDB,db:AsyncSession):
    projects = await db.execute(select(ProjectMemberDB).filter(ProjectMemberDB.user_id == user.id))
    return projects.scalars().all()

async def get_project_id_services(id:int,user:UserDB,db:AsyncSession):
    await get_role(id,"viewer",user,db)
    stmt = await db.execute(select(ProjectMemberDB).filter((ProjectMemberDB.user_id == user.id),(ProjectMemberDB.project_id ==id)))
    result = stmt.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")
    return result

async def update_project_services(id:int,project:ProjectDB,user:UserDB,db:AsyncSession):
    await get_role(id,"owner",user,db)
    result = await db.execute(select(ProjectDB).filter(ProjectDB.id == id))
    prod = result.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")
    
    if prod.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="You are not owner")
   
    await db.execute(update(ProjectDB).filter(ProjectDB.id == id).values(name = project.name,description = project.description))
    await db.commit()
    return "Success"
    
async def delete_project_services(id:int,user:UserDB,db:AsyncSession):
    await get_role(id,"owner",user,db)
    result = await db.execute(select(ProjectDB).filter(ProjectDB.id == id))
    prod = result.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")
    
    if prod.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="You are not owner")
   
    await db.execute(delete(ProjectDB).filter(ProjectDB.id ==id))
    await db.commit()
    return "Success"