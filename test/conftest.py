from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from main import app
from depends import get_db
from sqlalchemy import delete
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schemas.dbmodels import CommentDB, ProjectDB, ProjectMemberDB, TaskDB, UserDB


TEST_DATABASE_URL_ASYNC = "postgresql+asyncpg://postgres:123qwe@localhost:5432/Task_Manager_DB_test"
TEST_DATABASE_URL_SYNC = "postgresql+psycopg2://postgres:123qwe@localhost:5432/Task_Manager_DB_test"

async_engine = create_async_engine(TEST_DATABASE_URL_ASYNC)
AsyncSessionLocal = async_sessionmaker(async_engine)
engine = create_engine(TEST_DATABASE_URL_SYNC)
Session = sessionmaker(engine)
async def override_db():
    async with AsyncSessionLocal() as db:
        yield db

def clear_tables():
    with Session() as db:
        db.execute(delete(CommentDB))
        db.execute(delete(TaskDB))
        db.execute(delete(ProjectMemberDB))
        db.execute(delete(ProjectDB))
        db.execute(delete(UserDB))
        db.commit() 
       
@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_db] = override_db
    clear_tables()
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def create_users(client):
    
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    client.post("/user/register", json={"email": "editor@test.com", "password": "pass12345", "fullname": "Editor", "role":"editor"})
    client.post("/user/register", json={"email": "viewer@test.com", "password": "pass12345", "fullname": "Viewer", "role":"viewer"})

    owner = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    editor = client.post("/user/login", data={"username": "editor@test.com", "password": "pass12345"})
    viewer = client.post("/user/login", data={"username": "viewer@test.com", "password": "pass12345"})

    owner_token = owner.json()["access_token"]
    editor_token = editor.json()["access_token"]
    viewer_token = viewer.json()["access_token"]

    project = client.post("/project/create",
    json={"name":"Test project","description":"test description","owner_email":"owner@test.com"},
    headers={"Authorization": f"Bearer {owner_token}"})

    project_id = project.json()["id"]

    client.post(f"/project_member/project/{project_id}/member/editor@test.com", json={"role": "editor"}, headers={"Authorization": f"Bearer {owner_token}"})
    client.post(f"/project_member/project/{project_id}/member/viewer@test.com", json={"role": "viewer"}, headers={"Authorization": f"Bearer {owner_token}"})

    return {
        "project_id": project_id,
        "owner_token": owner_token,
        "editor_token": editor_token,
        "viewer_token": viewer_token,
    }