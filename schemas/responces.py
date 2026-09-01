from pydantic import BaseModel,ConfigDict
from datetime import datetime

class ProjectRESPONCES(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name : str
    description : str

class TaskRESPONCES(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    title : str
    description : str
    status : str 
    priority : str   
    deadline : datetime
    project_id : int
    assignee_id : int

class CommentRESPONCES(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id : int
    text : str
    task_id : int
    user_id : int

class AttachmentRESPONCES(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    content_type: str
    size_bytes: int
    uploaded_by: int
    created_at: datetime