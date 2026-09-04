from schemas.models import UserMODELS
from depends import get_db,get_current_user
from fastapi import APIRouter,Depends,UploadFile,BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from services.files import upload_file_services,download_file_services
from fastapi.responses import StreamingResponse
from config import settings
import minio

router = APIRouter(prefix="/file", tags=["files"])

@router.post("/upload")
async def upload_file(file: UploadFile, task_id:int, user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    return await upload_file_services(file,file.filename,task_id,user,db)

@router.get("/download")
async def download_file(filename:str, task_id:int, user:UserMODELS = Depends(get_current_user),db:AsyncSession = Depends(get_db)):
    file = await download_file_services(filename,task_id,user,db)
    customer = minio.Minio(settings.MINIO_ENDPOINT, settings.MINIO_ACCESS_KEY, settings.MINIO_SECRET_KEY, secure=False)
    response = customer.get_object(settings.MINIO_BUCKET, file.file_path)
    return StreamingResponse(response, media_type=file.content_type, headers={"Content-Disposition": f'attachment; filename="{file.filename}"'},background=BackgroundTasks(response.close))