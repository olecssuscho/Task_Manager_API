def test_get_project(client,create_users):
    result = client.get(f"/project/{create_users["project_id"]}",
                        headers={"Authorization":f"Bearer {create_users["editor_token"]}"})
    assert result.status_code == 200

def test_get_project_with_wrong_id(client,create_users):
    result = client.get(f"/project/{0}",headers={"Authorization":f"Bearer {create_users["editor_token"]}"})
    assert result.status_code == 404

def test_update_project_with_wrong_project_id(client,create_users):
    result = client.put(f"/project/{0}",json={"name":"foo","description":"bar"},
                        headers={"Authorization":f"Bearer {create_users["editor_token"]}"})
    assert result.status_code == 404

def test_update_project_with_wrong_user_id(client,create_users):
    result = client.put(f"/project/{create_users["project_id"]}",
                        json={"name":"foo","description":"bar"},headers={"Authorization":f"Bearer {create_users["editor_token"]}"})
    assert result.status_code == 405