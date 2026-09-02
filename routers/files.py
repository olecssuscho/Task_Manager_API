from schemas.models import UserMODELS
from depends import get_db,get_current_user
from fastapi import APIRouter,Depends,UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from services.files import upload_file_services,download_file_services
from fastapi.responses import FileResponse

router = APIRouter(prefix="/file", tags=["files"])

@router.post("/upload")
async def upload_file(file: UploadFile, task_id:int, project_id:int, user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await upload_file_services(file,file.filename,task_id,project_id,user,db)

@router.get("/download")
async def download_file(filename:str, task_id:int, project_id:int, user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    file = await download_file_services(filename,task_id,project_id,user,db)
    return FileResponse(
        path=file.file_path,
        filename=file.filename,
        media_type=file.content_type
    )