from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from auth import create_access_token,create_refresh_token, hash_token
from schemas.dbmodels import RefreshDB, UserDB
import services.ai_client as ai_client
from conftest import engine
from sqlalchemy import delete, select,update

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

def test_refresh_endpoint_with_access_token(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    token = owner.json()["access_token"]
    refresh_token = client.post("/user/refresh",headers={"Authorization":f"Bearer {token}"})
    
    assert refresh_token.status_code == 401 

def test_refresh_endpoint_with_worng_token(client):

    refresh_token = client.post("/user/refresh",headers={"Authorization":"Bearer sdasdwwwqw"})
    
    assert refresh_token.status_code == 401

def test_refresh_endpoint_with_not_exist_token(client):
    token = create_refresh_token({"email":"ss@test.com"})

    refresh_token = client.post("/user/refresh",headers={"Authorization":f"Bearer {token}"})
    
    assert refresh_token.status_code == 401

def test_refresh_when_user_not_found_returns_401(client,monkeypatch):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    refr_token = owner.json()["refresh_token"]
    
    async def fake_get_user(*args, **kwargs):
        return None
    monkeypatch.setattr("services.users.get_user", fake_get_user)
    refresh_token = client.post("/user/refresh",headers={"Authorization":f"Bearer {refr_token}"})
    
    assert refresh_token.status_code == 401 

def test_refresh_after_user_deleted_returns_401(client):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    assert owner.status_code == 200
    access_token = owner.json()["access_token"]
    refresh_token = owner.json()["refresh_token"]

    me = client.get("/user/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me.status_code == 200
    owner_id = me.json()["id"]

    with engine.begin() as conn:
        deleted = conn.execute(delete(UserDB).where(UserDB.id == owner_id))
        tokens = conn.execute(
            select(RefreshDB).where(RefreshDB.user_id == owner_id)
        ).all()

    assert deleted.rowcount == 1
    assert tokens == []  

    me_after = client.get("/user/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_after.status_code == 401

    response = client.post("/user/refresh", headers={"Authorization": f"Bearer {refresh_token}"})
    assert response.status_code == 401

def test_refresh_endpoint_with_used_token(client):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    token = owner.json()["refresh_token"]

    refresh_token_1 = client.post("/user/refresh",headers={"Authorization":f"Bearer {token}"})
    assert refresh_token_1.status_code == 200

    refresh_token_2 = client.post("/user/refresh",headers={"Authorization":f"Bearer {token}"})
    assert refresh_token_2.status_code == 401
    with engine.begin() as conn:
        record = conn.execute(
            select(RefreshDB).where(RefreshDB.token_hash == hash_token(token))
        ).one()
        family = conn.execute(
            select(RefreshDB).where(RefreshDB.family_id == record.family_id)
        ).all()
    assert len(family) >= 2
    assert all(row.revoked_at is not None for row in family)

def test_refresh_endpoint_that_was_revorked(client):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    token = owner.json()["refresh_token"]
    test_token = hash_token(token)
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:      
        response = conn.execute(update(RefreshDB).where(RefreshDB.token_hash == test_token).values(revoked_at = now))
        assert response.rowcount == 1

    result = client.post("/user/refresh",headers={"Authorization":f"Bearer {token}"})
    assert result.status_code == 401
    assert "access_token" not in result.json()

def test_refresh_endpoint_that_was_expired(client):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    token = owner.json()["refresh_token"]

    bad_exp = datetime.now(timezone.utc) - timedelta(days = 20)
    with engine.begin() as conn:
        response = conn.execute(update(RefreshDB).where(RefreshDB.token_hash == hash_token(token)).values(exp = bad_exp))
        assert response.rowcount == 1

    result = client.post("/user/refresh",headers={"Authorization":f"Bearer {token}"})
    assert result.status_code == 401

def test_refresh_endpoint_that_on_edge_of_abs_edge(client):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    token = owner.json()["refresh_token"]
    test_token = hash_token(token)
    token = owner.json()["refresh_token"]
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:      
        response = conn.execute(update(RefreshDB).where(RefreshDB.token_hash == test_token).values(abs_edge = now))
        assert response.rowcount == 1

    result = client.post("/user/refresh",headers={"Authorization":f"Bearer {token}"})
    assert result.status_code == 401       

def test_refresh_race_condition_revokes_family_and_returns_401(client,monkeypatch):
    client.post("/user/register", json={"email": "ss@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "ss@test.com", "password": "pass12345"})
    token = owner.json()["refresh_token"]
    test_token = hash_token(token)
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:      
        response = conn.execute(select(RefreshDB).filter(RefreshDB.token_hash == test_token)).one()
        stale = SimpleNamespace(
            id=response.id, user_id=response.user_id, family_id=response.family_id,
            used=None, revoked_at=None, exp=response.exp, abs_edge=response.abs_edge)
        conn.execute(update(RefreshDB).where(RefreshDB.token_hash == test_token).values(used = now))
    async def fake_get_record(*args, **kwargs):
        return stale
    monkeypatch.setattr("services.users.get_refresh_record", fake_get_record)
    result = client.post("/user/refresh",headers={"Authorization":f"Bearer {token}"})    
    assert result.status_code == 401
    with engine.begin() as conn:
        record = conn.execute(
            select(RefreshDB).where(RefreshDB.token_hash == hash_token(token))
        ).one()
        family = conn.execute(
            select(RefreshDB).where(RefreshDB.family_id == record.family_id)
        ).all()
    assert len(family) >= 1
    assert all(row.revoked_at is not None for row in family)

def test_change_password(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    token = owner.json()["access_token"]
    changed_password = client.put("/user/change_password",json = {"old_password":"pass12345","new_password":"1111111111"},headers={"Authorization":f"Bearer {token}"})
    
    assert changed_password.status_code == 200     

def test_change_password_with_wrong_old_new_pasword(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    token = owner.json()["access_token"]
    changed_password = client.put("/user/change_password",json = {"old_password":"ss","new_password":"1111111111"},headers={"Authorization":f"Bearer {token}"})
    
    assert changed_password.status_code == 401 

def test_change_password_with_same_old_and_new_pasword(client):
    client.post("/user/register", json={"email": "owner@test.com", "password": "pass12345", "fullname": "Owner", "role":"owner"})
    owner = client.post("/user/login", data={"username": "owner@test.com", "password": "pass12345"})
    token = owner.json()["access_token"]
    changed_password = client.put("/user/change_password",json = {"old_password":"pass12345","new_password":"pass12345"},headers={"Authorization":f"Bearer {token}"})
    
    assert changed_password.status_code == 400 

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

def test_logout_without_token(client):
    logout = client.post("/user/logout",headers={"Authorization":"Bearer jshshhw"})

    assert logout.status_code == 200 

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