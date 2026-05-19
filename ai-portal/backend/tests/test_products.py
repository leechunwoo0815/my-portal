"""产品模块测试：CRUD + 权限"""
import pytest
from app.models import Product
from tests.conftest import auth_header


def create_product(db, title="Test Product", published=True, user_id=1):
    p = Product(
        title=title, content="# Product Content", summary="Summary",
        category="AI工具", is_published=published, author_id=user_id,
    )
    db.add(p); db.commit(); db.refresh(p)
    return p


class TestProducts:
    def test_list_empty(self, client):
        r = client.get("/api/v1/products/")
        assert r.status_code == 200
        assert r.json()["items"] == []

    def test_list_with_data(self, client, db, admin_user):
        create_product(db, "P1", user_id=admin_user.id)
        create_product(db, "P2", user_id=admin_user.id)
        r = client.get("/api/v1/products/")
        assert len(r.json()["items"]) == 2

    def test_get_existing(self, client, db, admin_user):
        p = create_product(db, "Product A", user_id=admin_user.id)
        r = client.get(f"/api/v1/products/{p.id}")
        assert r.status_code == 200
        assert r.json()["title"] == "Product A"

    def test_create_as_admin(self, client, admin_token):
        r = client.post("/api/v1/products/", json={
            "title": "New", "content": "Body", "category": "AI"
        }, headers=auth_header(admin_token))
        assert r.status_code == 201

    def test_create_as_user(self, client, user_token):
        r = client.post("/api/v1/products/", json={"title": "X", "content": "Y"},
                        headers=auth_header(user_token))
        assert r.status_code == 403

    def test_update_as_admin(self, client, db, admin_token, admin_user):
        p = create_product(db, user_id=admin_user.id)
        r = client.put(f"/api/v1/products/{p.id}", json={"title": "Upd"},
                       headers=auth_header(admin_token))
        assert r.status_code == 200

    def test_delete_as_admin(self, client, db, admin_token, admin_user):
        p = create_product(db, user_id=admin_user.id)
        r = client.delete(f"/api/v1/products/{p.id}", headers=auth_header(admin_token))
        assert r.status_code == 200
