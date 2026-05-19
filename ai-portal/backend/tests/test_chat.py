"""对话模块测试：conversation CRUD + pin (admin only)"""
import pytest
from app.models import Conversation
from tests.conftest import auth_header


def create_conversation(db, user_id=1):
    c = Conversation(title="Test Chat", model_name="deepseek:deepseek-v4-flash", user_id=user_id)
    db.add(c); db.commit(); db.refresh(c)
    return c


class TestChat:
    def test_list_conversations(self, client, db, admin_token):
        create_conversation(db)
        r = client.get("/api/v1/chat/conversations", headers=auth_header(admin_token))
        assert r.status_code == 200

    def test_create_conversation(self, client, admin_token):
        r = client.post("/api/v1/chat/conversations", json={
            "title": "New Chat", "model": "deepseek:deepseek-v4-flash"
        }, headers=auth_header(admin_token))
        assert r.status_code == 200
        assert "id" in r.json()

    def test_delete_conversation(self, client, db, admin_token):
        c = create_conversation(db)
        r = client.delete(f"/api/v1/chat/conversations/{c.id}", headers=auth_header(admin_token))
        assert r.status_code == 200

    def test_pin_conversation(self, client, db, admin_token):
        c = create_conversation(db)
        r = client.post(f"/api/v1/chat/conversations/{c.id}/pin", headers=auth_header(admin_token))
        assert r.status_code == 200
        assert r.json()["message"] == "已置顶"

    def test_unpin_conversation(self, client, db, admin_token):
        c = create_conversation(db)
        client.post(f"/api/v1/chat/conversations/{c.id}/pin", headers=auth_header(admin_token))
        r = client.post(f"/api/v1/chat/conversations/{c.id}/unpin", headers=auth_header(admin_token))
        assert r.status_code == 200
        assert r.json()["message"] == "已取消置顶"

    def test_pin_limit(self, client, db, admin_token):
        for i in range(5):
            c = create_conversation(db, user_id=1)
            client.post(f"/api/v1/chat/conversations/{c.id}/pin", headers=auth_header(admin_token))
        c6 = create_conversation(db, user_id=1)
        r = client.post(f"/api/v1/chat/conversations/{c6.id}/pin", headers=auth_header(admin_token))
        assert r.status_code == 409

    def test_normal_user_allowed(self, client, user_token):
        r = client.get("/api/v1/chat/conversations", headers=auth_header(user_token))
        assert r.status_code == 200
