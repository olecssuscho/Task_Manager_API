from pydantic import BaseModel

class UserMODELS(BaseModel):
    email : str
    password : str
    fullname : str