from sqlalchemy.ext.asyncio import create_async_engine,async_session 
from config import settings

async_engine = create_async_engine(url = settings.DB_URL, echo = True , autocommit=False , autoflush = False)

async_Session = async_session()