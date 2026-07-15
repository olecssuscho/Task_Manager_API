from jose import JWTError, jwt 
from config import settings
from passlib.context import CryptContext  
from datetime import datetime,timedelta,timezone

contex = CryptContext(schemes=["argon2","bcrypt"], deprecated = "auto")

def hash_password(password:str)->str:
    return contex.hash(password)

def check_password(password:str,password_to_check:str)->bool:
    return contex.verify(password,password_to_check)

def create_refresh_token(data:dict)->str:
    to_encode = data.copy()
    to_encode.update({"type":"refresh"})
    exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_TIME_DAYS)
    to_encode.update({"exp":exp})
    return jwt.encode(to_encode,settings.SECRET_KEY,settings.ALGHORITHM)

def create_access_token(data:dict)->str:
    to_encode = data.copy()
    to_encode.update({"type":"access"})
    exp = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_TIME_DAYS)
    to_encode.update({"exp":exp})
    return jwt.encode(to_encode,settings.SECRET_KEY,settings.ALGHORITHM)

def decode_token(token:str)->dict:
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,settings.ALGHORITHM)
        return payload
    except JWTError:
        return None