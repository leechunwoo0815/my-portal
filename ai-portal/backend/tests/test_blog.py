"""博客模块测试：CRUD + 权限"""
import pytest
from app.core.security import get_password_hash
from app.models import Blog, User
from tests.conftest import auth_header


def create_blog_in_db(db, title="Test Blog", published=True):
    """辅助函数：直接在 DB 创建博客"""
    blog = Blog(
        title=title,
        content="# Test Content",
        summary="Test summary",
        category="测试",
        is_published=published,
        view_count=0,
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


class TestListBlogs:
    def test_list_empty(self, client):
        """空库 → 返回空列表"""
        r = client.get("/api/v1/blog/posts")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_list_with_data(self, client, db):
        """有数据 → 返回列表 + total"""
        create_blog_in_db(db, "Blog 1")
        create_blog_in_db(db, "Blog 2")
        r = client.get("/api/v1/blog/posts")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_only_published(self, client, db):
        """未发布的不出现在公开列表"""
        create_blog_in_db(db, "Published", published=True)
        create_blog_in_db(db, "Draft", published=False)
        r = client.get("/api/v1/blog/posts")
        data = r.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Published"

    def test_list_pagination(self, client, db):
        """分页正确"""
        for i in range(5):
            create_blog_in_db(db, f"Blog {i}")
        r = client.get("/api/v1/blog/posts", params={"page": 1, "page_size": 2})
        data = r.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1


class TestGetBlog:
    def test_get_existing(self, client, db):
        """获取存在的博客 → 200"""
        blog = create_blog_in_db(db, "My Blog")
        r = client.get(f"/api/v1/blog/posts/{blog.id}")
        assert r.status_code == 200
        assert r.json()["title"] == "My Blog"

    def test_get_increments_view(self, client, db):
        """获取博客 → 浏览量 +1"""
        blog = create_blog_in_db(db)
        r = client.get(f"/api/v1/blog/posts/{blog.id}")
        assert r.json()["view_count"] == 1

    def test_get_nonexistent(self, client):
        """获取不存在的 → 404"""
        r = client.get("/api/v1/blog/posts/99999")
        assert r.status_code == 404

    def test_get_unpublished(self, client, db):
        """未发布的 → 404"""
        blog = create_blog_in_db(db, "Draft", published=False)
        r = client.get(f"/api/v1/blog/posts/{blog.id}")
        assert r.status_code == 404


class TestCreateBlog:
    def test_create_as_admin(self, client, admin_token):
        """Admin 创建博客 → 200"""
        r = client.post("/api/v1/blog/posts", json={
            "title": "New Blog",
            "content": "Content here",
            "category": "AI",
        }, headers=auth_header(admin_token))
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "New Blog"
        assert data["category"] == "AI"

    def test_create_as_normal_user(self, client, user_token):
        """普通用户创建 → 403"""
        r = client.post("/api/v1/blog/posts", json={
            "title": "Unauthorized",
            "content": "Content",
        }, headers=auth_header(user_token))
        assert r.status_code == 403

    def test_create_without_auth(self, client):
        """未登录创建 → 401"""
        r = client.post("/api/v1/blog/posts", json={
            "title": "No Auth",
            "content": "Content",
        })
        assert r.status_code == 401

    def test_create_missing_fields(self, client, admin_token):
        """缺少必填字段 → 422"""
        r = client.post("/api/v1/blog/posts", json={
            "title": "Only Title",
        }, headers=auth_header(admin_token))
        assert r.status_code == 422


class TestUpdateBlog:
    def test_update_as_admin(self, client, db, admin_token):
        """Admin 更新博客 → 200 + 数据变更"""
        blog = create_blog_in_db(db, "Original")
        r = client.put(f"/api/v1/blog/posts/{blog.id}", json={
            "title": "Updated Title",
        }, headers=auth_header(admin_token))
        assert r.status_code == 200
        assert r.json()["title"] == "Updated Title"

    def test_update_nonexistent(self, client, admin_token):
        """更新不存在的 → 404"""
        r = client.put("/api/v1/blog/posts/99999", json={
            "title": "X",
        }, headers=auth_header(admin_token))
        assert r.status_code == 404

    def test_update_as_normal_user(self, client, db, user_token):
        """普通用户更新 → 403"""
        blog = create_blog_in_db(db)
        r = client.put(f"/api/v1/blog/posts/{blog.id}", json={
            "title": "Hacked",
        }, headers=auth_header(user_token))
        assert r.status_code == 403


class TestDeleteBlog:
    def test_delete_as_admin(self, client, db, admin_token):
        """Admin 删除博客 → 200"""
        blog = create_blog_in_db(db)
        r = client.delete(f"/api/v1/blog/posts/{blog.id}", headers=auth_header(admin_token))
        assert r.status_code == 200

    def test_delete_nonexistent(self, client, admin_token):
        """删除不存在的 → 404"""
        r = client.delete("/api/v1/blog/posts/99999", headers=auth_header(admin_token))
        assert r.status_code == 404

    def test_delete_as_normal_user(self, client, db, user_token):
        """普通用户删除 → 403"""
        blog = create_blog_in_db(db)
        r = client.delete(f"/api/v1/blog/posts/{blog.id}", headers=auth_header(user_token))
        assert r.status_code == 403


class TestAdminListBlogs:
    def test_admin_list_includes_unpublished(self, client, db, admin_token):
        """Admin 列表包含未发布"""
        create_blog_in_db(db, "Published", published=True)
        create_blog_in_db(db, "Draft", published=False)
        r = client.get("/api/v1/blog/admin/posts", headers=auth_header(admin_token))
        assert r.status_code == 200
        assert r.json()["total"] == 2

    def test_admin_list_requires_auth(self, client):
        """Admin 列表需要认证"""
        r = client.get("/api/v1/blog/admin/posts")
        assert r.status_code == 401
