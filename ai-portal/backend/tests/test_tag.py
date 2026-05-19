import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

ADMIN_TOKEN = None


def get_admin_headers():
    global ADMIN_TOKEN
    if ADMIN_TOKEN is None:
        res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        assert res.status_code == 200
        ADMIN_TOKEN = res.json()["access_token"]
    return {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def unique_slug():
    return f"tag-{uuid.uuid4().hex[:8]}"


class TestTag:
    def test_list_tags(self):
        res = client.get("/api/v1/tag/")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data or isinstance(data, list)

    def test_create_tag(self):
        slug = unique_slug()
        res = client.post("/api/v1/tag/", json={
            "name": f"TestTag-{slug}",
            "slug": slug,
        }, headers=get_admin_headers())
        assert res.status_code == 200
        assert res.json()["name"] == f"TestTag-{slug}"

    def test_popular_tags(self):
        res = client.get("/api/v1/tag/popular?limit=10")
        assert res.status_code == 200

    def test_update_tag(self):
        slug = unique_slug()
        create_res = client.post("/api/v1/tag/", json={
            "name": f"TestTag-{slug}",
            "slug": slug,
        }, headers=get_admin_headers())
        tag_id = create_res.json()["id"]
        res = client.put(f"/api/v1/tag/{tag_id}", json={"name": f"Updated-{slug}"}, headers=get_admin_headers())
        assert res.status_code == 200
        assert "Updated" in res.json()["name"]

    def test_delete_tag(self):
        slug = unique_slug()
        create_res = client.post("/api/v1/tag/", json={
            "name": f"ToDelete-{slug}",
            "slug": slug,
        }, headers=get_admin_headers())
        tag_id = create_res.json()["id"]
        res = client.delete(f"/api/v1/tag/{tag_id}", headers=get_admin_headers())
        assert res.status_code == 200

    def test_delete_nonexistent_tag(self):
        res = client.delete("/api/v1/tag/99999", headers=get_admin_headers())
        assert res.status_code == 404

    def test_unauthorized_create(self):
        res = client.post("/api/v1/tag/", json={"name": "未授权", "slug": unique_slug()})
        assert res.status_code == 401
