"""阅读历史模块测试"""
import pytest


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestReadingHistory:
    """阅读历史功能"""

    def _create_blog(self, client, admin_token):
        resp = client.post("/api/v1/blog/posts", headers=_auth(admin_token), json={
            "title": "测试博客", "content": "内容", "is_published": True,
        })
        return resp.json()["id"]

    def test_record_read(self, client, user_token, admin_token):
        blog_id = self._create_blog(client, admin_token)

        resp = client.post(f"/api/v1/history/?content_type=blog&content_id={blog_id}", headers=_auth(user_token))
        assert resp.status_code == 200
        assert resp.json()["message"] == "ok"

    def test_record_read_without_auth(self, client):
        resp = client.post("/api/v1/history/?content_type=blog&content_id=1")
        assert resp.status_code in (401, 403)

    def test_record_read_updates_existing(self, client, user_token, admin_token):
        blog_id = self._create_blog(client, admin_token)

        # 第一次记录
        client.post(f"/api/v1/history/?content_type=blog&content_id={blog_id}", headers=_auth(user_token))
        # 第二次记录（应该更新 read_at）
        resp = client.post(f"/api/v1/history/?content_type=blog&content_id={blog_id}", headers=_auth(user_token))
        assert resp.status_code == 200

    def test_list_history(self, client, user_token, admin_token):
        blog_id = self._create_blog(client, admin_token)
        client.post(f"/api/v1/history/?content_type=blog&content_id={blog_id}", headers=_auth(user_token))

        resp = client.get("/api/v1/history/", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["items"][0]["content_type"] == "blog"
        assert data["items"][0]["content_title"] == "测试博客"

    def test_list_history_pagination(self, client, user_token, admin_token):
        for i in range(5):
            blog_id = self._create_blog(client, admin_token)
            client.post(f"/api/v1/history/?content_type=blog&content_id={blog_id}", headers=_auth(user_token))

        resp = client.get("/api/v1/history/?page=1&page_size=2", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 5

    def test_list_history_filter_by_type(self, client, user_token, admin_token):
        blog_id = self._create_blog(client, admin_token)
        client.post(f"/api/v1/history/?content_type=blog&content_id={blog_id}", headers=_auth(user_token))

        resp = client.get("/api/v1/history/?content_type=blog", headers=_auth(user_token))
        assert resp.status_code == 200
        assert all(item["content_type"] == "blog" for item in resp.json()["items"])

    def test_clear_history(self, client, user_token, admin_token):
        blog_id = self._create_blog(client, admin_token)
        client.post(f"/api/v1/history/?content_type=blog&content_id={blog_id}", headers=_auth(user_token))

        resp = client.delete("/api/v1/history/", headers=_auth(user_token))
        assert resp.status_code == 204

        resp = client.get("/api/v1/history/", headers=_auth(user_token))
        assert resp.json()["total"] == 0

    def test_clear_history_by_type(self, client, user_token, admin_token):
        blog_id = self._create_blog(client, admin_token)
        client.post(f"/api/v1/history/?content_type=blog&content_id={blog_id}", headers=_auth(user_token))

        resp = client.delete("/api/v1/history/?content_type=news", headers=_auth(user_token))
        assert resp.status_code == 204

        # blog 历史应该还在
        resp = client.get("/api/v1/history/?content_type=blog", headers=_auth(user_token))
        assert resp.json()["total"] >= 1

    def test_history_without_auth(self, client):
        resp = client.get("/api/v1/history/")
        assert resp.status_code in (401, 403)

    def test_clear_history_without_auth(self, client):
        resp = client.delete("/api/v1/history/")
        assert resp.status_code in (401, 403)
