async def test_viewer_can_read_project(client, create_users):
    resp = await client.get(f"/project/{create_users['project_id']}", headers={"Authorization": f"Bearer {create_users['viewer_token']}"})
    assert resp.status_code == 200

async def test_viewer_cannot_create_task(client, create_users):
    resp = await client.post("/task/create", json={"title": "Test Task", "description": "Test Task Description","status": "todo",
                                                   "priority": "low", "deadline": "2023-12-31", "project_id": create_users['project_id'],
                                                   "assignee_email": "testuser2@gmail.com"}, headers={"Authorization": f"Bearer {create_users['viewer_token']}"})
    assert resp.status_code == 403

async def test_editor_can_create_task(client, create_users):
    resp = await client.post("/task/create", json={"title": "Test Task",
        "description": "Test Task Description",
        "status": "todo",
        "priority": "low",
        "deadline": "2023-12-31",
        "project_id": create_users["project_id"],
        "assignee_email": "testuser2@gmail.com",}, headers={"Authorization": f"Bearer {create_users['editor_token']}"})
    assert resp.status_code == 200