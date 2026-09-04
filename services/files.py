import os 
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.dbmodels import AttachmentDB, TaskDB,UserDB
from fastapi import UploadFile,status,HTTPException
from sqlalchemy import select
from config import settings
from depends import get_role
import mimetypes


async def upload_file_services(file:UploadFile, original_filename:str, task_id:int, user:UserDB, db:AsyncSession):

    task = await db.execute(select(TaskDB).filter(TaskDB.id == task_id))

    task_db = task.scalar_one_or_none()

    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    project_id = task_db.project_id

    if not project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    await get_role(project_id,"editor",user,db)

    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="File size too big")

    extension = os.path.splitext(original_filename)[1]
    uniq_name = f"{uuid4()}{extension}"

    content = await file.read()

    path = os.path.join(settings.UPLOAD_DIR,uniq_name)

    with open(path, "wb") as f:
        f.write(content)

    content_type,_ = mimetypes.guess_type(path)
    if not content_type:
        content_type = "application/octet-stream"

    file_db = AttachmentDB(
        filename = file.filename,
        file_path = path,
        content_type = content_type,
        size_bytes = file.size,
        task_id = task_id,
        uploaded_by = user.id
    )

    db.add(file_db)
    await db.commit()
    return "Success"

async def download_file_services(original_filename:str, task_id:int, user:UserDB, db:AsyncSession):

    task = await db.execute(select(TaskDB).filter(TaskDB.id == task_id))
    
    task_db = task.scalar_one_or_none()

    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    project_id = task_db.project_id

    if not project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    file = await db.execute(select(AttachmentDB).filter(AttachmentDB.filename == original_filename,AttachmentDB.task_id == task_id))

    file_real = file.scalar_one_or_none()

    if not file_real:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File is not found")

    await get_role(project_id,"viewer",user,db)

    return file_real

    