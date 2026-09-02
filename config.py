import os
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    DB_URL:str
    DB_URL_SYNC:str
    REDIS_URL:str
    REFRESH_TOKEN_TIME_DAYS:int
    ACCESS_TOKEN_TIME_MINUTES:int
    ALGORITHM:str
    SECRET_KEY:str
    UPLOAD_DIR: str 
    MAX_FILE_SIZE:int
    model_config = ConfigDict(env_file = ".env.local", env_file_encoding = "utf-8")

settings = Settings()