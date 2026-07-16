from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.dbmodels import ProjectDB, UserDB

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
