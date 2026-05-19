import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestSearch:
    def test_search_with_keyword(self):
        res = client.get("/api/v1/search/?keyword=AI")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data

    def test_search_with_type_filter(self):
        res = client.get("/api/v1/search/?keyword=AI&target_type=blog")
        assert res.status_code == 200
        data = res.json()
        if data["items"]:
            for item in data["items"]:
                assert item["target_type"] == "blog"

    def test_search_empty_keyword(self):
        res = client.get("/api/v1/search/?keyword=")
        assert res.status_code == 422

    def test_search_pagination(self):
        res = client.get("/api/v1/search/?keyword=AI&page=1&page_size=5")
        assert res.status_code == 200
        data = res.json()
        assert data["page_size"] == 5 or len(data["items"]) <= 5

    def test_search_no_results(self):
        res = client.get("/api/v1/search/?keyword=zzzznonexistent12345")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["items"] == []
