"""方案模块测试：CRUD + 权限"""
import pytest
from app.models import Solution
from tests.conftest import auth_header


def create_solution(db, title="Test Solution", published=True, user_id=1):
    s = Solution(
        title=title, content="# Solution Content", summary="Summary",
        category="智慧城市", is_published=published, author_id=user_id,
    )
    db.add(s); db.commit(); db.refresh(s)
    return s


class TestSolutions:
    def test_list_empty(self, client):
        r = client.get("/api/v1/solutions/")
        assert r.status_code == 200
        assert r.json()["items"] == []

    def test_list_with_data(self, client, db, admin_user):
        create_solution(db, "S1", user_id=admin_user.id)
        create_solution(db, "S2", user_id=admin_user.id)
        r = client.get("/api/v1/solutions/")
        assert len(r.json()["items"]) == 2

    def test_get_existing(self, client, db, admin_user):
        s = create_solution(db, "Solution A", user_id=admin_user.id)
        r = client.get(f"/api/v1/solutions/{s.id}")
        assert r.status_code == 200
        assert r.json()["title"] == "Solution A"

    def test_create_as_admin(self, client, admin_token):
        r = client.post("/api/v1/solutions/", json={
            "title": "New", "content": "Body", "category": "智慧城市"
        }, headers=auth_header(admin_token))
        assert r.status_code == 201

    def test_create_as_user(self, client, user_token):
        r = client.post("/api/v1/solutions/", json={"title": "X", "content": "Y"},
                        headers=auth_header(user_token))
        assert r.status_code == 403

    def test_update_as_admin(self, client, db, admin_token, admin_user):
        s = create_solution(db, user_id=admin_user.id)
        r = client.put(f"/api/v1/solutions/{s.id}", json={"title": "Upd"},
                       headers=auth_header(admin_token))
        assert r.status_code == 200

    def test_delete_as_admin(self, client, db, admin_token, admin_user):
        s = create_solution(db, user_id=admin_user.id)
        r = client.delete(f"/api/v1/solutions/{s.id}", headers=auth_header(admin_token))
        assert r.status_code == 200
