from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from config import settings

async_engine = create_async_engine(url = settings.DB_URL, echo = True)

Async_Session_Local = async_sessionmaker(async_engine,autocommit=False, autoflush=False)