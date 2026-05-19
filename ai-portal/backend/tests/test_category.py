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
    return f"test-{uuid.uuid4().hex[:8]}"


class TestCategory:
    def test_list_categories(self):
        res = client.get("/api/v1/category/")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data or isinstance(data, list)

    def test_create_category(self):
        slug = unique_slug()
        res = client.post("/api/v1/category/", json={
            "name": "测试分类",
            "slug": slug,
            "module_type": "blog",
            "sort_order": 0,
        }, headers=get_admin_headers())
        assert res.status_code == 200
        data = res.json()
        assert data["name"] == "测试分类"
        assert data["slug"] == slug

    def test_create_category_duplicate_slug(self):
        slug = unique_slug()
        client.post("/api/v1/category/", json={
            "name": "重复分类A",
            "slug": slug,
            "module_type": "blog",
        }, headers=get_admin_headers())
        res = client.post("/api/v1/category/", json={
            "name": "重复分类B",
            "slug": slug,
            "module_type": "blog",
        }, headers=get_admin_headers())
        assert res.status_code in (400, 409, 422, 500)

    def test_update_category(self):
        slug = unique_slug()
        create_res = client.post("/api/v1/category/", json={
            "name": "待更新",
            "slug": slug,
            "module_type": "news",
        }, headers=get_admin_headers())
        cat_id = create_res.json()["id"]
        res = client.put(f"/api/v1/category/{cat_id}", json={
            "name": "已更新",
        }, headers=get_admin_headers())
        assert res.status_code == 200
        assert res.json()["name"] == "已更新"

    def test_delete_category(self):
        slug = unique_slug()
        create_res = client.post("/api/v1/category/", json={
            "name": "待删除",
            "slug": slug,
            "module_type": "blog",
        }, headers=get_admin_headers())
        cat_id = create_res.json()["id"]
        res = client.delete(f"/api/v1/category/{cat_id}", headers=get_admin_headers())
        assert res.status_code == 200

    def test_delete_nonexistent_category(self):
        res = client.delete("/api/v1/category/99999", headers=get_admin_headers())
        assert res.status_code == 404

    def test_unauthorized_create(self):
        res = client.post("/api/v1/category/", json={
            "name": "未授权",
            "slug": unique_slug(),
            "module_type": "blog",
        })
        assert res.status_code == 401

    def test_category_tree(self):
        res = client.get("/api/v1/category/tree?module_type=blog")
        assert res.status_code == 200
