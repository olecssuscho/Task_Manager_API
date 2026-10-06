from conftest import client,create_users
import services.ai_client as ai_client

def fake_embedding(text):
    return [0.0] * 1024  

ai_client.generate_embedding = fake_embedding

def test_cannot_create_task_with_non_exist_assigne(client,create_users):
    task = client.post("/task/create",json={
          "title": "test_task",
          "description": "test description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "project_id": create_users["project_id"],
          "assignee_email": "poo@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    )

    assert task.status_code == 404   

def test_cannot_create_task_with_non_exist_project(client,create_users):
    task = client.post("/task/create",json={
          "title": "test_task",
          "description": "test description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "project_id": "3",
          "assignee_email": "editor@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    )

    assert task.status_code == 404  

def test_editor_cannot_update_task_with_non_assige_email(client,create_users):
    task = client.post("/task/create",json={
          "title": "test_task",
          "description": "test description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "project_id": create_users["project_id"],
          "assignee_email": "editor@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    )
    
    response = client.put(f"/task/{task.json()["id"]}",json={
          "title": "test_update_task",
          "description": "test update description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "assignee_email": "11111"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    ) 
    assert 404 == response.status_code

def test_editor_cannot_update_task_with_non_exist_task(client,create_users):
    task = client.post("/task/create",json={
          "title": "test_task",
          "description": "test description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "project_id": create_users["project_id"],
          "assignee_email": "editor@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    )
    
    response = client.put(f"/task/8",json={
          "title": "test_update_task",
          "description": "test update description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "assignee_email": "11111"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    ) 
    assert 404 == response.status_code

def test_editor_cannot_delete_task_with_non_exist_task(client,create_users):
    task = client.post("/task/create",json={
          "title": "test_task",
          "description": "test description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "project_id": create_users["project_id"],
          "assignee_email": "editor@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    )
    
    response = client.delete(f"/task/8",
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    ) 
    tasks = client.get(f"task/{create_users['project_id']}/tasks",
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"})

    assert task.json()["id"] not in tasks.json()
    assert 404 == response.status_code