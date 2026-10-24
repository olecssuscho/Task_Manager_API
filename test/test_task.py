from datetime import datetime, timedelta, timezone
import services.ai_client as ai_client

def fake_embedding(text):
    return [0.0] * 1024  

ai_client.generate_embedding = fake_embedding

def test_cannot_create_task_with_non_exist_assigne(create_task):
    task = create_task(assignee_email = "poo@test.com")

    assert task.status_code == 404   

def test_cannot_create_task_with_non_exist_project(create_task):
    task = create_task(project_id = 23)

    assert task.status_code == 404  

def test_editor_cannot_update_task_with_non_assige_email_data_is_kept(client,create_users,existing_task):

    task_id = existing_task["id"]
    
    response = client.put(f"/task/{task_id}",json={
          "title": "test_update_task",
          "description": "test update description",
          "status": "todo",
          "priority": "low",
          "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
          "assignee_email": "11111@eamil.com"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    ) 

    repeated_tasks = client.get(f"/task/{create_users["project_id"]}/tasks",headers={"Authorization":f"Bearer {create_users["editor_token"]}"})
    repeat_task = repeated_tasks.json().get("items")["id"==task_id]

    assert repeat_task["title"] == existing_task["title"]
    assert repeat_task["description"] == existing_task["description"]
    assert repeat_task["deadline"] == existing_task["deadline"]
    assert repeat_task["assignee_id"] == existing_task["assignee_id"]
    assert 404 == response.status_code

def test_editor_cannot_get_tas_for_not_exist_project(client,create_users):
    repeated_tasks = client.get(f"/task/{0}/tasks",headers={"Authorization":f"Bearer {create_users["editor_token"]}"})
    assert repeated_tasks.status_code == 404

    
