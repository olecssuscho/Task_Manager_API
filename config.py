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
    model_config = ConfigDict(env_file = ".env", env_file_encoding = "utf-8")

settings = Settings()