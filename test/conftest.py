import os
os.environ["TESTING"] = "1"

import pytest_asyncio
import schemas.dbmodels as models
from depends import get_db
from main import app
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import delete
from schemas.dbmodels import Base
from httpx import AsyncClient, ASGITransport

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:123qwe@localhost:5432/Task_Manager_DB_test"

@pytest_asyncio.fixture(autouse=True)
async def clear_db():
    engine = create_async_engine(url=TEST_DATABASE_URL, echo=True)  
    Session = async_sessionmaker(engine, autocommit=False, autoflush=False)

    async def override_get_db():
        async with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with Session() as db:
        await db.execute(delete(models.CommentDB))
        await db.execute(delete(models.TaskDB))
        await db.execute(delete(models.ProjectMemberDB))
        await db.execute(delete(models.ProjectDB))
        await db.execute(delete(models.UserDB))
        await db.commit()

    await engine.dispose() 

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def create_users(client):
    await client.post("/user/register",json={"email":"testuser1@gmail.com","password":"testpassword1","fullname":"Test User 1","role":"owner"})
    await client.post("/user/register",json={"email":"testuser2@gmail.com","password":"testpassword2","fullname":"Test User 2","role":"editor"})
    await client.post("/user/register",json={"email":"testuser3@gmail.com","password":"testpassword3","fullname":"Test User 3","role":"viewer"})

    owner = await client.post("/user/login",data={"username":"testuser1@gmail.com","password":"testpassword1"})
    editor = await client.post("/user/login",data={"username":"testuser2@gmail.com","password":"testpassword2"})
    viewer = await client.post("/user/login",data={"username":"testuser3@gmail.com","password":"testpassword3"})

    owner_token = owner.json()["access_token"]
    editor_token = editor.json()["access_token"]    
    viewer_token = viewer.json()["access_token"]

    create_resp = await client.post("/project/create",json={"name":"testproject1","description":"testproject1 description","owner_email":"testuser1@gmail.com"}, headers={"Authorization": f"Bearer {owner_token}"})
    project_id = create_resp.json()["id"]

    resp = await client.post(f"/project_member/project/{project_id}/member/testuser2@gmail.com",json={"role":"editor"}, headers={"Authorization": f"Bearer {owner_token}"})
    print(resp.status_code, resp.json())
    await client.post(f"/project_member/project/{project_id}/member/testuser3@gmail.com",json={"role":"viewer"}, headers={"Authorization": f"Bearer {owner_token}"})

    return {"project_id": project_id, "owner_token": owner_token, "editor_token": editor_token, "viewer_token": viewer_token}