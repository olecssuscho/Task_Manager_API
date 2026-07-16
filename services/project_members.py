from sqlalchemy import select
from fastapi import HTTPException,status
from schemas.dbmodels import ProjectDB,UserDB,ProjectMemberDB
from sqlalchemy.ext.asyncio import AsyncSession

async def add_member_services(project_id:int,user:UserDB,db:AsyncSession):
    stmt = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    if stmt.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    else:
        project_member_db = ProjectMemberDB(
            project_id = project_id,
            user_id = user.id,
            role = user.role
        )
        db.add(project_member_db)
        await db.commit()
        await db.refresh(project_member_db)
        return project_member_db