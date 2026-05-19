"""专栏模块测试"""
import pytest


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestSeriesCRUD:
    """专栏 CRUD 操作"""

    def test_create_series(self, client, user_token):
        resp = client.post("/api/v1/series/", headers=_auth(user_token), json={
            "title": "Python 进阶教程",
            "description": "从入门到精通",
            "cover_image": "/uploads/series/cover.png",
            "is_public": True,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Python 进阶教程"
        assert data["description"] == "从入门到精通"
        assert data["is_public"] is True
        assert "id" in data

    def test_create_series_without_auth(self, client):
        resp = client.post("/api/v1/series/", json={
            "title": "未认证专栏",
            "description": "应该失败",
        })
        assert resp.status_code in (401, 403)

    def test_list_series(self, client, user_token):
        # 创建两个专栏
        client.post("/api/v1/series/", headers=_auth(user_token), json={
            "title": "专栏1", "description": "描述1", "is_public": True,
        })
        client.post("/api/v1/series/", headers=_auth(user_token), json={
            "title": "专栏2", "description": "描述2", "is_public": True,
        })

        resp = client.get("/api/v1/series/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2

    def test_list_series_pagination(self, client, user_token):
        for i in range(5):
            client.post("/api/v1/series/", headers=_auth(user_token), json={
                "title": f"专栏{i}", "description": f"描述{i}", "is_public": True,
            })

        resp = client.get("/api/v1/series/?page=1&page_size=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 5
        assert data["total_pages"] >= 3

    def test_get_series_detail(self, client, user_token):
        create_resp = client.post("/api/v1/series/", headers=_auth(user_token), json={
            "title": "详情测试", "description": "详细描述", "is_public": True,
        })
        series_id = create_resp.json()["id"]

        resp = client.get(f"/api/v1/series/{series_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "详情测试"
        assert "articles" in data

    def test_get_nonexistent_series(self, client):
        resp = client.get("/api/v1/series/99999")
        assert resp.status_code == 404

    def test_update_series(self, client, user_token):
        create_resp = client.post("/api/v1/series/", headers=_auth(user_token), json={
            "title": "原始标题", "description": "原始描述", "is_public": True,
        })
        series_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/series/{series_id}", headers=_auth(user_token), json={
            "title": "更新后标题",
            "description": "更新后描述",
        })
        assert resp.status_code == 200
        assert resp.json()["title"] == "更新后标题"
        assert resp.json()["description"] == "更新后描述"

    def test_update_series_not_owner(self, client, user_token, admin_token):
        create_resp = client.post("/api/v1/series/", headers=_auth(user_token), json={
            "title": "他人专栏", "description": "描述", "is_public": True,
        })
        series_id = create_resp.json()["id"]

        resp = client.put(f"/api/v1/series/{series_id}", headers=_auth(admin_token), json={
            "title": "尝试修改",
        })
        assert resp.status_code in (403, 400)

    def test_delete_series(self, client, user_token):
        create_resp = client.post("/api/v1/series/", headers=_auth(user_token), json={
            "title": "待删除", "description": "描述", "is_public": True,
        })
        series_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/series/{series_id}", headers=_auth(user_token))
        assert resp.status_code == 204

        resp = client.get(f"/api/v1/series/{series_id}")
        assert resp.status_code == 404

    def test_delete_series_not_owner(self, client, user_token, admin_token):
        create_resp = client.post("/api/v1/series/", headers=_auth(user_token), json={
            "title": "他人专栏", "description": "描述", "is_public": True,
        })
        series_id = create_resp.json()["id"]

        resp = client.delete(f"/api/v1/series/{series_id}", headers=_auth(admin_token))
        assert resp.status_code in (403, 400)


class TestSeriesArticles:
    """专栏文章管理"""

    def _create_series(self, client, token):
        resp = client.post("/api/v1/series/", headers=_auth(token), json={
            "title": "测试专栏", "description": "描述", "is_public": True,
        })
        return resp.json()["id"]

    def _create_blog(self, client, admin_token):
        resp = client.post("/api/v1/blog/posts", headers=_auth(admin_token), json={
            "title": "测试博客", "content": "内容", "is_published": True,
        })
        return resp.json()["id"]

    def test_add_article_to_series(self, client, user_token, admin_token):
        series_id = self._create_series(client, user_token)
        blog_id = self._create_blog(client, admin_token)

        resp = client.post(f"/api/v1/series/{series_id}/articles", headers=_auth(user_token), json={
            "blog_id": blog_id,
            "order": 1,
        })
        assert resp.status_code == 200
        assert resp.json()["message"] == "添加成功"

    def test_add_duplicate_article(self, client, user_token, admin_token):
        series_id = self._create_series(client, user_token)
        blog_id = self._create_blog(client, admin_token)

        client.post(f"/api/v1/series/{series_id}/articles", headers=_auth(user_token), json={
            "blog_id": blog_id, "order": 1,
        })
        resp = client.post(f"/api/v1/series/{series_id}/articles", headers=_auth(user_token), json={
            "blog_id": blog_id, "order": 2,
        })
        assert resp.status_code == 200
        assert resp.json()["message"] == "文章已在专栏中"

    def test_remove_article_from_series(self, client, user_token, admin_token):
        series_id = self._create_series(client, user_token)
        blog_id = self._create_blog(client, admin_token)

        client.post(f"/api/v1/series/{series_id}/articles", headers=_auth(user_token), json={
            "blog_id": blog_id, "order": 1,
        })
        resp = client.delete(f"/api/v1/series/{series_id}/articles/{blog_id}", headers=_auth(user_token))
        assert resp.status_code == 204

    def test_series_detail_includes_articles(self, client, user_token, admin_token):
        series_id = self._create_series(client, user_token)
        blog_id = self._create_blog(client, admin_token)

        client.post(f"/api/v1/series/{series_id}/articles", headers=_auth(user_token), json={
            "blog_id": blog_id, "order": 1,
        })
        resp = client.get(f"/api/v1/series/{series_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["articles"]) >= 1
        assert data["articles"][0]["id"] == blog_id

    def test_add_article_not_owner(self, client, user_token, admin_token):
        series_id = self._create_series(client, user_token)
        blog_id = self._create_blog(client, admin_token)

        resp = client.post(f"/api/v1/series/{series_id}/articles", headers=_auth(admin_token), json={
            "blog_id": blog_id, "order": 1,
        })
        assert resp.status_code in (403, 400)

    def test_list_series_by_author(self, client, user_token, normal_user):
        client.post("/api/v1/series/", headers=_auth(user_token), json={
            "title": "用户专栏", "description": "描述", "is_public": True,
        })

        resp = client.get(f"/api/v1/series/?author_id={normal_user.id}")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1
