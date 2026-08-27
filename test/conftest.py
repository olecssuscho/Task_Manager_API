from httpx2 import AsyncClient,ASGITransport
import pytest_asyncio
import schemas.dbmodels as models
from depends import get_db
from main import app
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy import delete
from schemas.dbmodels import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:123qwe@localhost:5432/Task_Manager_DB_test"

async_engine = create_async_engine(url = TEST_DATABASE_URL, echo = True)

Test_Async_Session = async_sessionmaker(async_engine,autocommit=False, autoflush=False)

async def test_get_db():
    async with Test_Async_Session() as db:
        yield db

app.dependency_overrides[get_db] = test_get_db

@pytest_asyncio.fixture(autouse=True)
async def clear_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with Test_Async_Session() as db:
        await db.execute(delete(models.CommentDB))
        await db.execute(delete(models.TaskDB))
        await db.execute(delete(models.ProjectMemberDB))
        await db.execute(delete(models.ProjectDB))
        await db.execute(delete(models.UserDB))
        await db.commit()

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac