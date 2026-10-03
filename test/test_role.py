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
    