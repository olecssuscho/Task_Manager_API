import os 
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.dbmodels import AttachmentDB, TaskDB,UserDB
from fastapi import UploadFile,status,HTTPException
from sqlalchemy import select
from config import settings


async def upload_file_services(file:UploadFile, original_filename:str, id:int, project_id:int, user:UserDB, db:AsyncSession):

    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail="File size too big")

    stmt = await db.execute(select(TaskDB).filter(TaskDB.id == id, TaskDB.project_id == project_id))

    if not stmt.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task or project not found")

    extension = os.path.splitext(original_filename)[1]
    uniq_name = f"{uuid4()}{extension}"

    content = await file.read()

    path = os.path.join(settings.UPLOAD_DIR,uniq_name)

    with open(path, "wb") as f:
        f.write(content)

    file_db = AttachmentDB(
        filename = file.filename,
        file_path = path,
        content_type = extension,
        size_bytes = file.size,
        task_id = id,
        uploaded_by = user.id
    )

    db.add(file_db)
    await db.commit()
    return "Success"
