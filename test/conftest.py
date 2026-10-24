from datetime import datetime, timedelta, timezone
import os
os.environ["TESTING"] = "1"
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from main import app
from depends import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from schemas.dbmodels import Base
from sqlalchemy.pool import NullPool

TEST_DATABASE_URL_ASYNC = "postgresql+asyncpg://postgres:123qwe@localhost:5432/Task_Manager_DB_test"
TEST_DATABASE_URL_SYNC = "postgresql+psycopg2://postgres:123qwe@localhost:5432/Task_Manager_DB_test"

async_engine = create_async_engine(TEST_DATABASE_URL_ASYNC,poolclass = NullPool)
AsyncSessionLocal = async_sessionmaker(async_engine)
engine = create_engine(TEST_DATABASE_URL_SYNC)
async def override_db():
    async with AsyncSessionLocal() as db:
        yield db

@pytest.fixture(scope="session",autouse=True)
def prepare_tables():
    Base.metadata.create_all(bind = engine)
    yield
    Base.metadata.drop_all(bind = engine)

@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())

@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
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

@pytest.fixture
def create_task(client,create_users):
    def _create(
        title="test",
        description="test description",
        status="todo",
        priority="low",
        deadline=None,
        project_id=None,
        assignee_email="editor@test.com",
        token=None,
    ):

        if deadline is None:
            deadline = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        if project_id is None:
            project_id = create_users["project_id"]
        if token is None:
            token = create_users["editor_token"]
    
        return client.post("/task/create",json={
              "title": title,
              "description": description,
              "status": status,
              "priority": priority,
              "deadline": deadline,
              "project_id": project_id,
              "assignee_email": assignee_email
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    
    return _create

@pytest.fixture
def existing_task(create_task):
    response = create_task()
    assert response.status_code == 200
    return response.json()