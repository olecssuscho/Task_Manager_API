from conftest import client,create_users
import services.ai_client as ai_client

def fake_embedding(text):
    return [0.0] * 1024  

ai_client.generate_embedding = fake_embedding

def test_viewer_cannot_create_task(create_users,client):
    response = client.post("/task/create",json={
          "title": "test_task",
          "description": "test description",
          "status": "todo",
          "priority": "low",
          "deadline": "2026-10-05T13:35:04.076Z",
          "project_id": create_users["project_id"],
          "assignee_email": "editor@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"}
    ) 
    assert 403 == response.status_code

def test_viewer_cannot_update_task(create_users,client):
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
          "project_id": create_users["project_id"],
          "assignee_email": "editor@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"}
    ) 
    assert 403 == response.status_code

def test_viewer_cannot_delete_task(create_users,client):
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
    
    response = client.delete(f"/task/{task.json()["id"]}",
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"}
    ) 
    assert 403 == response.status_code

def test_viewer_can_see_task(create_users,client):
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
    
    response = client.get(f"/task/{create_users["project_id"]}/tasks",
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"}
    ) 
    assert 200 == response.status_code

def test_editor_can_create_task(client,create_users):
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

    assert task.status_code == 200

def test_editor_can_update_task(client,create_users):
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
          "project_id": create_users["project_id"],
          "assignee_email": "editor@test.com"
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    ) 
    assert 200 == response.status_code

def test_editor_can_delete_task(client,create_users):
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
    response = client.delete(f"/task/{task.json()["id"]}",
            headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
        ) 
    assert 200 == response.status_code

def test_viewer_cannot_create_comment(create_users,client):
    task = client.post("/task/create",json={
              "title": "test_task",
              "description": "test description",
              "status": "todo",
              "priority": "low",
              "deadline": "2026-10-05T13:35:04.076Z",
              "project_id": create_users["project_id"],
              "assignee_email": "editor@test.com"
            },
            headers={"Authorization": f"Bearer {create_users["editor_token"]}"})

    id = task.json()["id"]

    comm = client.post(f"/comment/task/{id}/comment",json={
          "text": "test text",
        },
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"}
    ) 
    assert comm.status_code == 403

def test_viewer_can_see_comment(create_users,client):
    task = client.post("/task/create",json={
              "title": "test_task",
              "description": "test description",
              "status": "todo",
              "priority": "low",
              "deadline": "2026-10-05T13:35:04.076Z",
              "project_id": create_users["project_id"],
              "assignee_email": "editor@test.com"
            },
            headers={"Authorization": f"Bearer {create_users["editor_token"]}"})

    id = task.json()["id"]

    comm = client.get(f"/comment/task/{id}/comments",
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"}
    ) 
    assert comm.status_code == 200

def test_viewer_cannot_delete_comment(create_users,client):
    task = client.post("/task/create",json={
              "title": "test_task",
              "description": "test description",
              "status": "todo",
              "priority": "low",
              "deadline": "2026-10-05T13:35:04.076Z",
              "project_id": create_users["project_id"],
              "assignee_email": "editor@test.com"
            },
            headers={"Authorization": f"Bearer {create_users["editor_token"]}"})

    id = task.json()["id"]

    comm_to_create = client.post(f"/comment/task/{id}/comment",json={
              "text": "test text",
            },
            headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
        )
    
    comm = client.delete(f"/comment/{comm_to_create.json()["id"]}",
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"}
    ) 
    assert comm.status_code == 403

def test_editor_can_create_comment(create_users,client):
    task = client.post("/task/create",json={
              "title": "test_task",
              "description": "test description",
              "status": "todo",
              "priority": "low",
              "deadline": "2026-10-05T13:35:04.076Z",
              "project_id": create_users["project_id"],
              "assignee_email": "editor@test.com"
            },
            headers={"Authorization": f"Bearer {create_users["editor_token"]}"})

    id = task.json()["id"]

    comm = client.post(f"/comment/task/{id}/comment",json={
          "text": "test text",
        },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    ) 
    assert comm.status_code == 200

def test_editor_can_delete_comment(create_users,client):
    task = client.post("/task/create",json={
              "title": "test_task",
              "description": "test description",
              "status": "todo",
              "priority": "low",
              "deadline": "2026-10-05T13:35:04.076Z",
              "project_id": create_users["project_id"],
              "assignee_email": "editor@test.com"
            },
            headers={"Authorization": f"Bearer {create_users["editor_token"]}"})

    id = task.json()["id"]

    comm_to_create = client.post(f"/comment/task/{id}/comment",json={
                  "text": "test text",
                },
                headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
        )
    
    comm = client.delete(f"/comment/{comm_to_create.json()["id"]}",
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"}
    ) 
    assert comm.status_code == 200

def test_viewer_cannot_add_member(client,create_users):
    member = client.post(f"/project_member/project/{create_users["project_id"]}/member/editor@test.com", json={"role": "editor"}, headers={"Authorization": f"Bearer {create_users["viewer_token"]}"})
    assert member.status_code == 403

def test_viewer_cannot_patch_member(client,create_users):
    member = client.patch(f"/project_member/project/{create_users["project_id"]}/member/editor@test.com", json={"role": "owner"}, headers={"Authorization": f"Bearer {create_users["viewer_token"]}"})
    assert member.status_code == 403

def test_viewer_delete_patch_member(client,create_users):
    member = client.delete(f"/project_member/project/{create_users["project_id"]}/member/editor@test.com",  headers={"Authorization": f"Bearer {create_users["viewer_token"]}"})
    assert member.status_code == 403

def test_editor_cannot_add_member(client,create_users):
    member = client.post(f"/project_member/project/{create_users["project_id"]}/member/viewer@test.com", json={"role": "editor"}, headers={"Authorization": f"Bearer {create_users["editor_token"]}"})
    assert member.status_code == 403

def test_editor_cannot_patch_member(client,create_users):
    member = client.patch(f"/project_member/project/{create_users["project_id"]}/member/viewer@test.com", json={"role": "owner"}, headers={"Authorization": f"Bearer {create_users["editor_token"]}"})
    assert member.status_code == 403

def test_editor_cannot_delete__member(client,create_users):
    member = client.delete(f"/project_member/project/{create_users["project_id"]}/member/viewer@test.com",  headers={"Authorization": f"Bearer {create_users["editor_token"]}"})
    assert member.status_code == 403

def test_owner_can_patch_member(client,create_users):
    member = client.patch(f"/project_member/project/{create_users["project_id"]}/member/viewer@test.com", json={"role": "owner"}, headers={"Authorization": f"Bearer {create_users["owner_token"]}"})
    assert member.status_code == 200

def test_owner_can_delete_member(client,create_users):
    member = client.delete(f"/project_member/project/{create_users["project_id"]}/member/viewer@test.com",  headers={"Authorization": f"Bearer {create_users["owner_token"]}"})
    assert member.status_code == 200

def test_viewer_can_create_project(client,create_users):
    project = client.post("/project/create",
    json={"name":"Test project","description":"test description","owner_email":"viewer@test.com"},
    headers={"Authorization": f"Bearer {create_users["viewer_token"]}"})
    assert project.status_code == 200

def test_viewer_can_get_project(client,create_users):
    project = client.get("/project/",
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"})
    assert project.status_code == 200

def test_viewer_cannot_update_project(client,create_users):
    project = client.put(f"/project/{create_users["project_id"]}",json={
        "name":"Updated project","description":"Updated description"
    },
        headers={"Authorization": f"Bearer {create_users["viewer_token"]}"})
    assert project.status_code == 403

def test_viewer_cannot_delete_project(client,create_users):
    project = client.delete(f"/project/{create_users["project_id"]}",
            headers={"Authorization": f"Bearer {create_users["viewer_token"]}"})
    assert project.status_code == 403

def test_editor_cannot_update_project(client,create_users):
    project = client.put(f"/project/{create_users["project_id"]}",json={
        "name":"Updated project","description":"Updated description"
    },
        headers={"Authorization": f"Bearer {create_users["editor_token"]}"})
    assert project.status_code == 403

def test_editor_cannot_delete_project(client,create_users):
    project = client.delete(f"/project/{create_users["project_id"]}",
            headers={"Authorization": f"Bearer {create_users["editor_token"]}"})
    assert project.status_code == 403

def test_owner_can_update_project(client,create_users):
    project = client.put(f"/project/{create_users["project_id"]}",json={
        "name":"Updated project","description":"Updated description"
    },
        headers={"Authorization": f"Bearer {create_users["owner_token"]}"})
    assert project.status_code == 200

def test_owner_can_delete_project(client,create_users):
    project = client.delete(f"/project/{create_users["project_id"]}",
            headers={"Authorization": f"Bearer {create_users["owner_token"]}"})
    assert project.status_code == 200

