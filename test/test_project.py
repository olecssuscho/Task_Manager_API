def test_get_project_with_wrong_id(client,create_users):
    result = client.get(f"/project/{0}",headers={"Authorization":f"Bearer {create_users["editor_token"]}"})
    assert result.status_code == 404