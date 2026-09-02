from schemas.models import UserMODELS
from depends import get_db,get_current_user
from fastapi import APIRouter,Depends,UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from services.files import upload_file_services

router = APIRouter(prefix="/file", tags=["files"])

@router.post("/upload")
async def upload_file(file: UploadFile, task_id:int, project_id:int, user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await upload_file_services(file,file.filename,task_id,project_id,user,db)