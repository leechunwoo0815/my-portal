"""评论模块测试：嵌套、点赞、级联删除"""
import pytest
from tests.conftest import auth_header


class TestComments:
    def test_create_comment(self, client, user_token):
        r = client.post("/api/v1/comments/blog/1", json={
            "content": "Great!", "emoji": "🎉"
        }, headers=auth_header(user_token))
        assert r.status_code == 200
        assert r.json()["author_name"] == "testuser"

    def test_list_comments(self, client, user_token):
        client.post("/api/v1/comments/blog/1", json={
            "content": "C1"
        }, headers=auth_header(user_token))
        client.post("/api/v1/comments/blog/1", json={
            "content": "C2"
        }, headers=auth_header(user_token))
        r = client.get("/api/v1/comments/blog/1")
        assert r.status_code == 200
        assert len(r.json()) >= 2

    def test_nested_reply(self, client, user_token):
        parent = client.post("/api/v1/comments/blog/1", json={
            "content": "Parent"
        }, headers=auth_header(user_token)).json()
        r = client.post("/api/v1/comments/blog/1", json={
            "content": "Reply", "parent_id": parent["id"]
        }, headers=auth_header(user_token))
        assert r.status_code == 200
        assert r.json()["parent_id"] == parent["id"]

    def test_like_comment(self, client, user_token):
        c = client.post("/api/v1/comments/blog/1", json={
            "content": "Like me"
        }, headers=auth_header(user_token)).json()
        r = client.post(f"/api/v1/comments/{c['id']}/like")
        assert r.status_code == 200
        assert r.json()["likes_count"] == 1
        r = client.post(f"/api/v1/comments/{c['id']}/like")
        assert r.status_code == 200
        assert r.json()["likes_count"] == 0

    def test_delete_comment(self, client, user_token):
        c = client.post("/api/v1/comments/blog/1", json={
            "content": "Delete me"
        }, headers=auth_header(user_token)).json()
        r = client.delete(f"/api/v1/comments/{c['id']}", headers=auth_header(user_token))
        assert r.status_code == 200

    def test_cascade_delete(self, client, user_token):
        parent = client.post("/api/v1/comments/blog/1", json={
            "content": "Parent"
        }, headers=auth_header(user_token)).json()
        child = client.post("/api/v1/comments/blog/1", json={
            "content": "Child", "parent_id": parent["id"]
        }, headers=auth_header(user_token)).json()
        r = client.delete(f"/api/v1/comments/{parent['id']}", headers=auth_header(user_token))
        assert r.status_code == 200
        # Verify both gone
        all_comments = client.get("/api/v1/comments/blog/1").json()
        ids = [c["id"] for c in all_comments]
        assert parent["id"] not in ids
        assert child["id"] not in ids
