"""认证模块测试：登录、当前用户、修改密码"""
import pytest
from app.core.security import get_password_hash
from tests.conftest import auth_header


class TestLogin:
    def test_login_success(self, client, db):
        """正确的用户名密码 → 200 + token"""
        from app.models import User
        user = User(
            username="admin",
            email="test@aiportal.local",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_admin=True,
        )
        db.add(user)
        db.commit()

        r = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, db):
        """密码错误 → 401"""
        from app.models import User
        user = User(
            username="admin",
            email="test@aiportal.local",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_admin=True,
        )
        db.add(user)
        db.commit()

        r = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrongpass",
        })
        assert r.status_code == 401

    def test_login_nonexistent_user(self, client):
        """用户不存在 → 401"""
        r = client.post("/api/v1/auth/login", json={
            "username": "nobody",
            "password": "pass",
        })
        assert r.status_code == 401

    def test_login_empty_body(self, client):
        """空请求体 → 422"""
        r = client.post("/api/v1/auth/login", json={})
        assert r.status_code == 422


class TestGetCurrentUser:
    def test_get_me_with_token(self, client, admin_user, admin_token):
        """有效 token → 返回用户信息"""
        r = client.get("/api/v1/auth/me", headers=auth_header(admin_token))
        assert r.status_code == 200
        data = r.json()
        assert data["username"] == "admin"
        assert data["is_admin"] is True

    def test_get_me_without_token(self, client):
        """无 token → 401"""
        r = client.get("/api/v1/auth/me")
        assert r.status_code == 401

    def test_get_me_invalid_token(self, client):
        """无效 token → 401"""
        r = client.get("/api/v1/auth/me", headers=auth_header("invalid.token.here"))
        assert r.status_code == 401


class TestChangePassword:
    def test_change_password_success(self, client, admin_user, admin_token):
        """正确旧密码 → 200"""
        r = client.put("/api/v1/auth/password", json={
            "old_password": "admin123",
            "new_password": "newpass123",
        }, headers=auth_header(admin_token))
        assert r.status_code == 200
        assert "message" in r.json()

    def test_change_password_wrong_old(self, client, admin_user, admin_token):
        """旧密码错误 → 401"""
        r = client.put("/api/v1/auth/password", json={
            "old_password": "wrongold",
            "new_password": "newpass123",
        }, headers=auth_header(admin_token))
        assert r.status_code == 401

    def test_change_password_no_auth(self, client):
        """未登录 → 401"""
        r = client.put("/api/v1/auth/password", json={
            "old_password": "old",
            "new_password": "new123456",
        })
        assert r.status_code == 401
