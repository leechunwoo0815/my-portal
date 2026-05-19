"""新闻模块测试：CRUD + 权限"""
import pytest
from app.models import News
from tests.conftest import auth_header


def create_news(db, title="Test News", published=True, user_id=1):
    news = News(
        title=title, content="# News Content", summary="Summary",
        category="AI", is_published=published, author_id=user_id,
    )
    db.add(news); db.commit(); db.refresh(news)
    return news


class TestNews:
    def test_list_empty(self, client):
        r = client.get("/api/v1/news/")
        assert r.status_code == 200
        assert r.json()["items"] == []

    def test_list_with_data(self, client, db, admin_user):
        create_news(db, "News 1", user_id=admin_user.id)
        create_news(db, "News 2", user_id=admin_user.id)
        r = client.get("/api/v1/news/")
        assert len(r.json()["items"]) == 2

    def test_get_existing(self, client, db, admin_user):
        n = create_news(db, "My News", user_id=admin_user.id)
        r = client.get(f"/api/v1/news/{n.id}")
        assert r.status_code == 200
        assert r.json()["title"] == "My News"

    def test_create_as_admin(self, client, admin_token):
        r = client.post("/api/v1/news/", json={
            "title": "New News", "content": "Body", "category": "AI"
        }, headers=auth_header(admin_token))
        assert r.status_code == 201

    def test_create_as_normal_user(self, client, user_token):
        r = client.post("/api/v1/news/", json={
            "title": "X", "content": "Y"
        }, headers=auth_header(user_token))
        assert r.status_code == 403

    def test_update_as_admin(self, client, db, admin_token, admin_user):
        n = create_news(db, user_id=admin_user.id)
        r = client.put(f"/api/v1/news/{n.id}", json={"title": "Updated"}, headers=auth_header(admin_token))
        assert r.status_code == 200

    def test_delete_as_admin(self, client, db, admin_token, admin_user):
        n = create_news(db, user_id=admin_user.id)
        r = client.delete(f"/api/v1/news/{n.id}", headers=auth_header(admin_token))
        assert r.status_code == 200
