"""作品集模块测试：CRUD + 权限"""
import pytest
from app.models import Project
from tests.conftest import auth_header


def create_project(db, title="Test Project", published=True):
    p = Project(
        title=title, description="Desc", content="# Content",
        category="智慧城市", is_published=published,
    )
    db.add(p); db.commit(); db.refresh(p)
    return p


class TestPortfolio:
    def test_list_empty(self, client):
        r = client.get("/api/v1/portfolio/projects")
        assert r.status_code == 200
        assert r.json()["total"] == 0

    def test_list_with_data(self, client, db):
        create_project(db, "P1")
        create_project(db, "P2")
        r = client.get("/api/v1/portfolio/projects")
        assert r.json()["total"] == 2

    def test_get_existing(self, client, db):
        p = create_project(db, "Project A")
        r = client.get(f"/api/v1/portfolio/projects/{p.id}")
        assert r.status_code == 200
        assert r.json()["title"] == "Project A"

    def test_create_as_admin(self, client, admin_token):
        r = client.post("/api/v1/portfolio/projects", json={
            "title": "New", "description": "Desc", "content": "Body", "category": "AI"
        }, headers=auth_header(admin_token))
        assert r.status_code == 200

    def test_create_as_user(self, client, user_token):
        r = client.post("/api/v1/portfolio/projects", json={
            "title": "X", "description": "D", "content": "C", "category": "AI"
        }, headers=auth_header(user_token))
        assert r.status_code == 403

    def test_update_as_admin(self, client, db, admin_token):
        p = create_project(db)
        r = client.put(f"/api/v1/portfolio/projects/{p.id}", json={"title": "Upd"},
                       headers=auth_header(admin_token))
        assert r.status_code == 200

    def test_delete_as_admin(self, client, db, admin_token):
        p = create_project(db)
        r = client.delete(f"/api/v1/portfolio/projects/{p.id}", headers=auth_header(admin_token))
        assert r.status_code == 200
