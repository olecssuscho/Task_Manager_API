def test_comment_where_task_id_is_wrong(client):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    token = owner.json()["access_token"]

    comment = client.post(f"/comment/task/{0}/comment",json={"text":"sea"},headers={"Authorization":f"Bearer {token}"})

    assert comment.status_code == 404