from datetime import timedelta
from auth import create_access_token,create_refresh_token
import services.ai_client as ai_client

def fake_embedding(text):
    return [0.0] * 1024  

ai_client.generate_embedding = fake_embedding

def test_exist_email(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    user =  client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    assert user.status_code == 409

def test_wrong_email_password(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    email =  client.post("/user/login", data={"username": "12222@test.com", "password": "pass12345"})
    password =  client.post("/user/login", data={"username": "owner@test.com", "password": "11"})
    assert email.status_code == 401
    assert password.status_code == 401

def test_without_token(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    token =  client.post("/project/create",
    json={"name":"Test project","description":"test description","owner_email":"owner@test.com"})

    assert token.status_code == 401

def test_with_rot_token(client):
    token = create_access_token(
        data={"sub": "owner@test.com"},
        expires_delta=timedelta(seconds=-1)
    )
    project =  client.post("/project/create",
    json={"name":"Test project","description":"test description","owner_email":"owner@test.com"},
    headers={"Authorization": f"Bearer {token}"})
    
    assert project.status_code == 401

def test_with_bad_token(client):
    token = create_access_token(
        data={"email": "owner@test.com"}
    )
    token +="1232"
    project =  client.post("/project/create",
    json={"name":"Test project","description":"test description","owner_email":"owner@test.com"},
    headers={"Authorization": f"Bearer {token}"})
    
    assert project.status_code == 401

def test_refresh_token(client):
    token = create_refresh_token(
        data={"email": "owner@test.com"}
    )
    project =  client.post("/project/create",
    json={"name":"Test project","description":"test description","owner_email":"owner@test.com"},
    headers={"Authorization": f"Bearer {token}"})
    
    assert project.status_code == 401

def test_refresh_endpoint(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    token = owner.json()["refresh_token"]
    refresh_token = client.post("user/refresh",headers={"Authorization":f"Bearer {token}"})
    
    assert refresh_token.status_code == 200   

def test_change_password(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    token = owner.json()["access_token"]
    changed_password = client.put("/user/change_password",json = {"old_password":"pass12345","new_password":"1111111111"},headers={"Authorization":f"Bearer {token}"})
    
    assert changed_password.status_code == 200     

def test_logout(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    token = owner.json()["refresh_token"]
    access_token = owner.json()["access_token"]
    logout = client.post("/user/logout",headers={"Authorization":f"Bearer {token}"})
    changed_password = client.put("/user/change_password",json = {"old_password":"pass12345","new_password":"1111111111"},
                                  headers={"Authorization":f"Bearer {access_token}"})

    assert logout.status_code == 200 
    assert changed_password.status_code == 200 

def test_logout_all(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner1 = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    owner2 = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    token1 = owner1.json()["access_token"]
    token2 = owner2.json()["access_token"]
    logout_all = client.post("/user/logout_all",headers={"Authorization":f"Bearer {token1}"})

    changed_password = client.put("/user/change_password",json = {"old_password":"pass12345","new_password":"1111111111"},
                                      headers={"Authorization":f"Bearer {token2}"})

    assert logout_all.status_code == 200
    assert changed_password.status_code == 200