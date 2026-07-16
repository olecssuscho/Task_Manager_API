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

