from conftest import client,create_users
import services.ai_client as ai_client

def test_owner_become_part_of_created_project(client,create_users):
    project = client.post("/project/create",
        json={"name":"Test project","description":"test description","owner_email":"owner@test.com"},
        headers={"Authorization": f"Bearer {create_users["owner_token"]}"})

    members = client.get(f"/project_member/project/{project.json()["id"]}/members", 
                headers={"Authorization": f"Bearer {create_users["owner_token"]}"})

    me = client.get("user/me",headers={"Authorization": f"Bearer {create_users["owner_token"]}"})
    members_correct = [user["user_id"] for user in members.json()["items"]]
    assert me.json()["id"] in members_correct

def test_owner_cannot_add_non_exist_person(client,create_users):
    member = client.post(f"/project_member/project/{create_users["project_id"]}/member/123454@test.com", json={"role": "editor"}, 
                          headers={"Authorization": f"Bearer {create_users['owner_token']}"})

    assert 404 == member.status_code

def test_owner_cannot_add_non_exist_project(client,create_users):
    member = client.post(f"/project_member/project/{23}/member/editor@test.com", json={"role": "editor"}, 
                          headers={"Authorization": f"Bearer {create_users['owner_token']}"})

    assert 404 == member.status_code