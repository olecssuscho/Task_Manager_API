from datetime import datetime, timedelta, timezone
from fastapi.websockets import WebSocketDisconnect
import pytest
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

