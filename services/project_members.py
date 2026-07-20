from sqlalchemy import select,delete,update
from fastapi import HTTPException,status
from schemas.dbmodels import ProjectDB,UserDB,ProjectMemberDB
from sqlalchemy.ext.asyncio import AsyncSession
from depends import get_role

async def add_member_id_services(project_id:int,user_id:int,role:ProjectMemberDB,user:UserDB,db:AsyncSession):
    await get_role(project_id,"owner",user,db)
    stmt = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    if stmt.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    user_db = await db.execute(select(UserDB).filter(UserDB.id == user_id))
    if not user_db.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    else:
        project_member_db = ProjectMemberDB(
            project_id = project_id,
            user_id = user_id,
            role = role.role
        )
        db.add(project_member_db)
        await db.commit()
        await db.refresh(project_member_db)
        return project_member_db  

async def delete_member_services(project_id:int,user_id:int,user:UserDB,db:AsyncSession):
    await get_role(project_id,"owner",user,db)
    stmt = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    result = stmt.scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    user_db = await db.execute(select(ProjectMemberDB).filter(ProjectMemberDB.project_id == project_id,ProjectMemberDB.user_id == user_id))
    if user_db.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    await db.execute(delete(ProjectMemberDB).filter(ProjectMemberDB.user_id == user_id))
    await db.commit()
    return "Success"

async def patch_member_services(project_id:int,user_id:int,role:ProjectMemberDB,user:UserDB,db:AsyncSession):
    await get_role(project_id,"owner",user,db)
    stmt = await db.execute(select(ProjectDB).filter(ProjectDB.id == project_id))
    result = stmt.scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project did not found")
    user_db = await db.execute(select(ProjectMemberDB).filter(ProjectMemberDB.user_id == user_id))
    if user_db.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User did not found")
    await db.execute(update(ProjectMemberDB).filter(ProjectMemberDB.project_id == project_id,ProjectMemberDB.user_id == user_id).values(role = role.role))
    await db.commit()
    return "Success" 
    