"""Refresh Token 测试"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _register_and_login(client: TestClient) -> dict:
    """注册并登录，返回 token 响应"""
    client.post("/api/v1/auth/register", json={
        "username": "refreshtest",
        "email": "refresh@test.com",
        "password": "test123456",
    })
    resp = client.post("/api/v1/auth/login", json={
        "username": "refreshtest",
        "password": "test123456",
    })
    return resp.json()


class TestRefreshToken:

    def test_login_returns_refresh_token(self, client):
        """登录应返回 access_token 和 refresh_token"""
        data = _register_and_login(client)
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_returns_new_tokens(self, client):
        """用 refresh_token 应能换取新的 token 对"""
        data = _register_and_login(client)
        resp = client.post("/api/v1/auth/refresh", json={
            "refresh_token": data["refresh_token"],
        })
        assert resp.status_code == 200
        new_data = resp.json()
        assert "access_token" in new_data
        assert "refresh_token" in new_data
        # 新的 token 应与旧的不同（rotation）
        assert new_data["refresh_token"] != data["refresh_token"]

    def test_old_refresh_token_invalidated_after_use(self, client):
        """使用过的 refresh_token 应被吊销，再次使用应失败"""
        data = _register_and_login(client)
        old_rt = data["refresh_token"]

        # 第一次刷新成功
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": old_rt})
        assert resp.status_code == 200

        # 用旧的 refresh_token 再次刷新应失败
        resp = client.post("/api/v1/auth/refresh", json={"refresh_token": old_rt})
        assert resp.status_code == 401

    def test_invalid_refresh_token_rejected(self, client):
        """无效的 refresh_token 应被拒绝"""
        resp = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid.token.here",
        })
        assert resp.status_code == 401

    def test_access_token_cannot_be_used_as_refresh(self, client):
        """access_token 不能当 refresh_token 用"""
        data = _register_and_login(client)
        resp = client.post("/api/v1/auth/refresh", json={
            "refresh_token": data["access_token"],
        })
        assert resp.status_code == 401

    def test_refresh_token_cannot_be_used_as_access(self, client):
        """refresh_token 不能当 access_token 用"""
        data = _register_and_login(client)
        headers = {"Authorization": f"Bearer {data['refresh_token']}"}
        resp = client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 401

    def test_new_access_token_works(self, client):
        """刷新后的新 access_token 应能正常使用"""
        data = _register_and_login(client)
        resp = client.post("/api/v1/auth/refresh", json={
            "refresh_token": data["refresh_token"],
        })
        new_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {new_token}"}
        resp = client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 200
