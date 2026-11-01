def test_comment_post_where_task_id_is_wrong(client):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    token = owner.json()["access_token"]

    comment = client.post(f"/comment/task/{0}/comment",json={"text":"sea"},headers={"Authorization":f"Bearer {token}"})

    assert comment.status_code == 404

def test_comment_get_where_task_id_is_wrong(client):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    token = owner.json()["access_token"]

    comment = client.get(f"/comment/task/{0}/comments",headers={"Authorization":f"Bearer {token}"})

    assert comment.status_code == 404

def test_comment_delete_where_task_id_is_wrong(client):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    token = owner.json()["access_token"]

    comment = client.delete(f"/comment/{0}",headers={"Authorization":f"Bearer {token}"})

    assert comment.status_code == 404