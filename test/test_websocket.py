from datetime import datetime, timedelta, timezone
from fastapi.websockets import WebSocketDisconnect
import pytest
from auth import create_access_token
from conftest import client,create_users
import services.ai_client as ai_client

def fake_embedding(text):
    return [0.0] * 1024  

ai_client.generate_embedding = fake_embedding

def test_websocket_users_receive_text(client, create_users):
    project_id = create_users["project_id"]
    editor_url = f"/ws/websocket/{create_users["editor_token"]}/{project_id}"
    owner_url = f"/ws/websocket/{create_users["owner_token"]}/{project_id}"

    with client.websocket_connect(editor_url) as ws_editor, \
         client.websocket_connect(owner_url) as ws_owner:

        response = client.post("/task/create", json={
            "title": "test",
            "description": "test",
            "status": "todo",
            "priority": "low",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "project_id": project_id,
            "assignee_email": "editor@test.com",
        }, headers={"Authorization":f"Bearer {create_users["owner_token"]}"})
        assert response.status_code == 200

        task_id = response.json()["id"]

        assert ws_editor.receive_text() == f"Task created: {task_id}"
        assert ws_owner.receive_text() == f"Task created: {task_id}"

def test_websocket_user_not_receive_text(client, create_users):
    project_id = create_users["project_id"]
    
    client.post("/user/register", json={"email": "notwebsocket@test.com", "password": "pass12345", "fullname": "Viewer", "role":"editor"})
    not_websocket = client.post("/user/login", data={"username": "notwebsocket@test.com", "password": "pass12345"})
    assert not_websocket.status_code == 200
    not_websocket_token = not_websocket.json()["access_token"]
    not_websocket_url = f"/ws/websocket/{not_websocket_token}/{project_id}"

    with pytest.raises(WebSocketDisconnect) as dis_info:
        with client.websocket_connect(not_websocket_url) as ws:
            pass
    assert dis_info.value.code

def test_websocket_double_connect(client, create_users):
    project_id = create_users["project_id"]
    editor_url = f"/ws/websocket/{create_users["editor_token"]}/{project_id}"
    owner_url = f"/ws/websocket/{create_users["owner_token"]}/{project_id}"

    with client.websocket_connect(editor_url) as ws_editor1, \
         client.websocket_connect(owner_url) as ws_owner, \
         client.websocket_connect(editor_url) as ws_editor2:

        response = client.post("/task/create", json={
            "title": "test",
            "description": "test",
            "status": "todo",
            "priority": "low",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "project_id": project_id,
            "assignee_email": "editor@test.com",
        }, headers={"Authorization":f"Bearer {create_users["owner_token"]}"})
        assert response.status_code == 200

        task_id = response.json()["id"]

        assert ws_editor1.receive_text() == f"Task created: {task_id}"
        assert ws_owner.receive_text() == f"Task created: {task_id}"
        assert ws_editor2.receive_text() == f"Task created: {task_id}"

@pytest.mark.parametrize("token",["ss","a.s.d"])
def test_websocket_rejects_malformed_token(client, create_users, token):
    project_id = create_users["project_id"]
    editor_url = f"/ws/websocket/{token}/{project_id}"

    with pytest.raises(WebSocketDisconnect) as dis_info:
        with client.websocket_connect(editor_url):
            pass
    assert dis_info.value.code == 1008

def test_websocket_rejects_wrong_paylod_token(client, create_users):
    project_id = create_users["project_id"]
    token = create_access_token(
        {"email":"fake"}
    )
    editor_url = f"/ws/websocket/{token}/{project_id}"

    with pytest.raises(WebSocketDisconnect) as dis_info:
        with client.websocket_connect(editor_url):
            pass
    assert dis_info.value.code == 1008

def test_websocket_rejects_wrong_exp_token(client, create_users):
    project_id = create_users["project_id"]
    token = create_access_token(
        data = {"email":"editor@test.com"},
        expires_delta=timedelta(-1)
    )
    editor_url = f"/ws/websocket/{token}/{project_id}"

    with pytest.raises(WebSocketDisconnect) as dis_info:
        with client.websocket_connect(editor_url):
            pass
    assert dis_info.value.code == 1008

def test_websocket_rejects_not_exist_project(client, create_users):
    project_id = -9
    
    editor_url = f"/ws/websocket/{create_users["editor_token"]}/{project_id}"

    with pytest.raises(WebSocketDisconnect) as dis_info:
        with client.websocket_connect(editor_url):
            pass
    assert dis_info.value.code == 1008    

def test_user_was_disconnected_but_get_message(client, create_users):
    project_id = create_users["project_id"]
    editor_url = f"/ws/websocket/{create_users["editor_token"]}/{project_id}"
    owner_url = f"/ws/websocket/{create_users["owner_token"]}/{project_id}"

    with client.websocket_connect(editor_url) as ws_editor:
        with client.websocket_connect(owner_url) :
            pass
        
        response = client.post("/task/create", json={
            "title": "test",
            "description": "test",
            "status": "todo",
            "priority": "low",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "project_id": project_id,
            "assignee_email": "editor@test.com",
        }, headers={"Authorization":f"Bearer {create_users["owner_token"]}"})
        assert response.status_code == 200

        task_id = response.json()["id"]

        assert ws_editor.receive_text() == f"Task created: {task_id}"

def test_websocket_user_not_part_of_project(client, create_users):
    project_id = create_users["project_id"]
    editor_url = f"/ws/websocket/{create_users["editor_token"]}/{project_id}"
    owner_url = f"/ws/websocket/{create_users["owner_token"]}/{project_id}"

    client.post("/user/register", json={"email": "notpartofproject1@test.com", "password": "pass12345", "fullname": "Viewer", "role":"editor"})
    not_part_of_project1 = client.post("/user/login", data={"username": "notpartofproject1@test.com", "password": "pass12345"})
    assert not_part_of_project1.status_code == 200
    not_part_of_project1_token = not_part_of_project1.json()["access_token"]

    project = client.post("/project/create",
    json={"name":"Test project","description":"test description","owner_email":"owner@test.com"},
    headers={"Authorization": f"Bearer {create_users["owner_token"]}"})
    project_id_2 = project.json()["id"]    

    client.post(f"/project_member/project/{project_id_2}/member/notpartofproject1@test.com", json={"role": "editor"}, headers={"Authorization": f"Bearer {create_users["owner_token"]}"})

    not_part_of_project1_url = f"/ws/websocket/{not_part_of_project1_token}/{project_id_2}"

    with client.websocket_connect(editor_url) as ws_editor, \
         client.websocket_connect(owner_url) as ws_owner, \
        client.websocket_connect(not_part_of_project1_url) as ws_not_project1_part:

        response1 = client.post("/task/create", json={
            "title": "test",
            "description": "test",
            "status": "todo",
            "priority": "low",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "project_id": project_id,
            "assignee_email": "editor@test.com",
        }, headers={"Authorization":f"Bearer {create_users["owner_token"]}"})
        assert response1.status_code == 200

        response2 = client.post("/task/create", json={
            "title": "test",
            "description": "test",
            "status": "todo",
            "priority": "low",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "project_id": project_id_2,
            "assignee_email": "notpartofproject1@test.com",
        }, headers={"Authorization":f"Bearer {not_part_of_project1_token}"})
        assert response2.status_code == 200

        task_id_2 = response2.json()["id"]

        assert ws_not_project1_part.receive_text() == f"Task created: {task_id_2}"

        response2 = client.put(f"/task/{task_id_2}", json={
            "title": "change",
            "description": "test",
            "status": "todo",
            "priority": "low",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "assignee_email": "notpartofproject1@test.com",
        }, headers={"Authorization":f"Bearer {not_part_of_project1_token}"})
        
        assert ws_not_project1_part.receive_text() == f"Task updated: {task_id_2}"
        assert ws_editor.receive_text() != f"Task updated: {task_id_2}"
        assert ws_owner.receive_text() != f"Task updated: {task_id_2}"

def test_websocket_user_deleted_from_project(client, create_users):
    project_id = create_users["project_id"]
    editor_url = f"/ws/websocket/{create_users["editor_token"]}/{project_id}"

    client.delete(f"/project_member/project/{project_id}/member/editor@test.com", headers={"Authorization": f"Bearer {create_users["owner_token"]}"})

    with pytest.raises(WebSocketDisconnect) as dis_info:
           with client.websocket_connect(editor_url):
               pass
    assert dis_info.value.code == 1008