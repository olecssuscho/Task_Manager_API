from conftest import create_users
def test_viewer_cannot_create_task(client,create_users):
    response = client.post("http://localhost:8000/task/create",json={
          "title": "test_task",
          "description": "test description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "project_id": 1,
          "assignee_email": "editor@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"}
    )
    assert 403 == response.status_code

def test_editor_can_create_task(client,create_users):
    response = client.post("http://localhost:8000/task/create",json={
          "title": "test_task",
          "description": "test description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "project_id": 1,
          "assignee_email": "editor@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    )
    assert 200 == response.status_code

def test_editor_cannot_delete_project(client,create_users):
    response = client.delete(f"http://localhost:8000/project/{create_users["project_id"]}",
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    )
    assert 403 == response.status_code