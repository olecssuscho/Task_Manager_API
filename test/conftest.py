import os
import pytest
import subprocess
import time
import requests
from schemas.dbmodels import Base
from sqlalchemy import create_engine


TEST_DATABASE_URL = "postgresql+psycopg2://postgres:123qwe@localhost:5432/Task_Manager_DB_test"

def prepare_db():
    sync_engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.drop_all(bind=sync_engine)
    Base.metadata.create_all(bind=sync_engine)
    sync_engine.dispose()

@pytest.fixture(scope="session", autouse=True)
def live_server():

    prepare_db()

    env={**os.environ, "TESTING": "1", "DB_URL":"TEST_DATABASE_URL"}

    proc = subprocess.Popen(["python", "-m", "uvicorn", "main:app", "--port", "8000"], env=env)
    for _ in range(20):
        try:
            requests.post("http://localhost:8000/",timeout=1)
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            time.sleep(0.5)

    yield
    proc.terminate()
    proc.wait()

@pytest.fixture
def client():
    return requests.Session()  

@pytest.fixture(scope="session" )
def create_users(live_server):
    base = "http://localhost:8000"
    s = requests.Session()

    s.post(f"{base}/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    s.post(f"{base}/user/register", json={"email": "editor@test.com", "password": "pass12345", "fullname": "Editor", "role":"editor"})
    s.post(f"{base}/user/register", json={"email": "viewer@test.com", "password": "pass12345", "fullname": "Viewer", "role":"viewer"})

    owner = s.post(f"{base}/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    editor = s.post(f"{base}/user/login", data={"username": "editor@test.com", "password": "pass12345"})
    viewer = s.post(f"{base}/user/login", data={"username": "viewer@test.com", "password": "pass12345"})

    owner_token = owner.json()["access_token"]
    editor_token = editor.json()["access_token"]
    viewer_token = viewer.json()["access_token"]

    project = s.post(f"{base}/project/create",
    json={"name":"Test project","description":"test description","owner_email":"owner@test.com"},
    headers={"Authorization": f"Bearer {owner_token}"})

    project_id = project.json()["id"]

    s.post(f"{base}/project_member/project/{project_id}/member/editor@test.com", json={"role": "editor"}, headers={"Authorization": f"Bearer {owner_token}"})
    s.post(f"{base}/project_member/project/{project_id}/member/viewer@test.com", json={"role": "viewer"}, headers={"Authorization": f"Bearer {owner_token}"})

    return {
        "project_id": project_id,
        "owner_token": owner_token,
        "editor_token": editor_token,
        "viewer_token": viewer_token,
    }