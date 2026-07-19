from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class UserMODELS(BaseModel):
    email : str
    password : str
    fullname : str
    role : Literal["viewer","editor","owner"]

class ProjectMODELS(BaseModel):
    name : str
    description : str
    owner_email : str

class ProjectUpdateMODELS(BaseModel):
    name : str
    description : str

class TaskMODELS(BaseModel):
    title : str
    description : str
    status : Literal["todo","in_progress","review","done"]
    priority : Literal["low","medium","high"]
    deadline : datetime
    project_id : int
    assignee_email : str

class ProjectMemberUpdateMODELS(BaseModel):
    role : Literal["viewer","editor","owner"]

class CommentMODELS(BaseModel):
    text : str
    user_id : int