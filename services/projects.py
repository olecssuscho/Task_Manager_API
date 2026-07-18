from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update,delete
from schemas.dbmodels import ProjectDB,UserDB,ProjectMemberDB

async def create_project_services(project:ProjectDB,user:UserDB,db:AsyncSession):
    owner = await db.execute(select(UserDB).filter(UserDB.email == user.email))
    owner_id_db = owner.scalar_one_or_none().id
    project_db = ProjectDB(
        name = project.name,
        description = project.description,
        owner_id = owner_id_db
    )
    db.add(project_db)
    await db.commit()
    await db.refresh(project_db)
    return project_db

async def get_project_services(user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(ProjectMemberDB).filter(ProjectMemberDB.user_id == user.id))
    result = stmt.scalars().all()
    return result

async def get_project_id_services(id:int,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(ProjectMemberDB).filter((ProjectMemberDB.user_id == user.id),(ProjectDB.id ==id)))
    result = stmt.scalars().all()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")
    return result

async def update_project_services(id:int,project:ProjectDB,user:UserDB,db:AsyncSession):
    result = await db.execute(select(ProjectDB).filter(ProjectDB.id == id))
    prod = result.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")
    
    if not prod.owner_id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="You are not owner")
   
    await db.execute(update(ProjectDB).values(name = project.name,description = project.description))
    await db.commit()
    return "Success"
    
async def delete_project_services(id:int,user:UserDB,db:AsyncSession):
    result = await db.execute(select(ProjectDB).filter(ProjectDB.id == id))
    prod = result.scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projects not found")
    
    if not prod.owner_id:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="You are not owner")
   
    await db.execute(delete(ProjectDB).filter(ProjectDB.id ==id))
    await db.commit()
    return "Success"