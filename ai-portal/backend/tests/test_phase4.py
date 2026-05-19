"""
Phase 4 自动化测试 - 互动、动态、通知、积分、社交
覆盖所有 Phase 4 新增模块的 API 端点
"""
import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token, get_password_hash
from app.models import User, Blog, Moment, UserLike, UserFavorite, UserFollow, Notification, PointLog


class TestInteraction:
    """互动模块测试 - 点赞/收藏/分享"""

    def test_toggle_like_blog(self, client, db, admin_user, admin_token):
        blog = Blog(title="Test Blog", content="Content", author_id=admin_user.id, is_published=True, likes_count=0)
        db.add(blog)
        db.commit()
        blog_id = blog.id

        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post(f"/api/v1/interaction/like/blog/{blog_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["liked"] is True

        res = client.post(f"/api/v1/interaction/like/blog/{blog_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["liked"] is False

    def test_like_status_unauthenticated(self, client, db, admin_user):
        blog = Blog(title="Test Blog2", content="Content", author_id=admin_user.id, is_published=True)
        db.add(blog)
        db.commit()
        blog_id = blog.id

        res = client.get(f"/api/v1/interaction/like-status/blog/{blog_id}")
        assert res.status_code in (200, 401)

    def test_toggle_favorite_blog(self, client, db, admin_user, admin_token):
        blog = Blog(title="Test Fav Blog", content="Content", author_id=admin_user.id, is_published=True, favorites_count=0)
        db.add(blog)
        db.commit()
        blog_id = blog.id

        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post(f"/api/v1/interaction/favorite/blog/{blog_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["favorited"] is True

        res = client.post(f"/api/v1/interaction/favorite/blog/{blog_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["favorited"] is False

    def test_favorite_status(self, client, db, admin_user, admin_token):
        blog = Blog(title="Fav Status Blog", content="Content", author_id=admin_user.id, is_published=True)
        db.add(blog)
        db.commit()
        blog_id = blog.id

        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get(f"/api/v1/interaction/favorite-status/blog/{blog_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "is_favorited" in data

    def test_list_my_favorites(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/v1/interaction/favorites", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data

    def test_share_content(self, client, db, admin_user, admin_token):
        blog = Blog(title="Share Blog", content="Content", author_id=admin_user.id, is_published=True, shares_count=0)
        db.add(blog)
        db.commit()
        blog_id = blog.id

        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post(f"/api/v1/interaction/share/blog/{blog_id}", headers=headers)
        assert res.status_code == 200
        assert res.json()["success"] is True

    def test_like_invalid_type(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/api/v1/interaction/like/invalid/1", headers=headers)
        assert res.status_code in (400, 404)


class TestMoment:
    """动态模块测试 - CRUD + 点赞 + 转发"""

    def test_create_moment(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post("/api/v1/moment/", json={"content": "Hello world!", "is_public": True}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["content"] == "Hello world!"
        assert data["moment_type"] == "original"

    def test_list_moments(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/v1/moment/", json={"content": "Moment 1", "is_public": True}, headers=headers)
        client.post("/api/v1/moment/", json={"content": "Moment 2", "is_public": True}, headers=headers)

        res = client.get("/api/v1/moment/", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2

    def test_list_moments_public(self, client, admin_user):
        headers = {"Authorization": f"Bearer {create_access_token(data={'sub': str(admin_user.id)})}"}
        client.post("/api/v1/moment/", json={"content": "Public moment", "is_public": True}, headers=headers)

        res = client.get("/api/v1/moment/")
        assert res.status_code == 200
        assert res.json()["total"] >= 1

    def test_get_moment_detail(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_res = client.post("/api/v1/moment/", json={"content": "Detail moment", "is_public": True}, headers=headers)
        moment_id = create_res.json()["id"]

        res = client.get(f"/api/v1/moment/{moment_id}", headers=headers)
        assert res.status_code == 200
        assert res.json()["content"] == "Detail moment"

    def test_update_moment(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_res = client.post("/api/v1/moment/", json={"content": "Before update", "is_public": True}, headers=headers)
        moment_id = create_res.json()["id"]

        res = client.put(f"/api/v1/moment/{moment_id}", json={"content": "After update"}, headers=headers)
        assert res.status_code == 200
        assert res.json()["content"] == "After update"

    def test_delete_moment(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_res = client.post("/api/v1/moment/", json={"content": "To delete", "is_public": True}, headers=headers)
        moment_id = create_res.json()["id"]

        res = client.delete(f"/api/v1/moment/{moment_id}", headers=headers)
        assert res.status_code == 200

        res = client.get(f"/api/v1/moment/{moment_id}", headers=headers)
        assert res.status_code == 404

    def test_like_moment(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_res = client.post("/api/v1/moment/", json={"content": "Like me", "is_public": True}, headers=headers)
        moment_id = create_res.json()["id"]

        res = client.post(f"/api/v1/moment/{moment_id}/like", headers=headers)
        assert res.status_code == 200
        assert res.json()["liked"] is True

        res = client.post(f"/api/v1/moment/{moment_id}/like", headers=headers)
        assert res.status_code == 200
        assert res.json()["liked"] is False

    def test_repost_moment(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        create_res = client.post("/api/v1/moment/", json={"content": "Original post", "is_public": True}, headers=headers)
        moment_id = create_res.json()["id"]

        res = client.post(f"/api/v1/moment/{moment_id}/repost", json={"content": "My comment"}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["moment_type"] == "repost"
        assert data["original_id"] == moment_id

    def test_my_moments(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/v1/moment/", json={"content": "My moment", "is_public": True}, headers=headers)

        res = client.get("/api/v1/moment/my", headers=headers)
        assert res.status_code == 200
        assert res.json()["total"] >= 1


class TestNotification:
    """通知模块测试 - 列表/已读/未读数"""

    def test_list_notifications(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/v1/notification/", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "unread_count" in data

    def test_mark_notification_read(self, client, db, admin_user, admin_token):
        notif = Notification(user_id=admin_user.id, type="system", title="Test", content="Hello", is_read=False)
        db.add(notif)
        db.commit()
        notif_id = notif.id

        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.put(f"/api/v1/notification/{notif_id}/read", headers=headers)
        assert res.status_code == 200

    def test_mark_all_read(self, client, db, admin_user, admin_token):
        db.add(Notification(user_id=admin_user.id, type="system", title="T1", is_read=False))
        db.add(Notification(user_id=admin_user.id, type="system", title="T2", is_read=False))
        db.commit()

        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.put("/api/v1/notification/read-all", headers=headers)
        assert res.status_code == 200

    def test_unread_count(self, client, db, admin_user, admin_token):
        db.add(Notification(user_id=admin_user.id, type="system", title="Unread", is_read=False))
        db.commit()

        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/v1/notification/unread-count", headers=headers)
        assert res.status_code == 200
        assert res.json()["unread_count"] >= 1


class TestPoint:
    """积分模块测试 - 记录/进度/排行"""

    def test_list_point_logs(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/v1/point/logs", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data

    def test_get_point_progress(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/v1/point/progress", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "level" in data
        assert "current_points" in data
        assert "level_title" in data

    def test_point_ranking(self, client, admin_user, admin_token):
        res = client.get("/api/v1/point/ranking")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data


class TestSocial:
    """社交模块测试 - 关注/粉丝/状态"""

    def test_follow_user(self, client, db, admin_user, normal_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post(f"/api/v1/social/follow/{normal_user.id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["is_following"] is True

    def test_unfollow_user(self, client, db, admin_user, normal_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post(f"/api/v1/social/follow/{normal_user.id}", headers=headers)
        res = client.post(f"/api/v1/social/follow/{normal_user.id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["is_following"] is False

    def test_cannot_follow_self(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.post(f"/api/v1/social/follow/{admin_user.id}", headers=headers)
        assert res.status_code in (400, 403)

    def test_follow_status(self, client, db, admin_user, normal_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get(f"/api/v1/social/follow-status/{normal_user.id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "is_following" in data
        assert "is_mutual" in data

    def test_follow_status_unauthenticated(self, client, normal_user):
        res = client.get(f"/api/v1/social/follow-status/{normal_user.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["is_following"] is False

    def test_list_followers(self, client, db, admin_user, normal_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post(f"/api/v1/social/follow/{normal_user.id}", headers=headers)

        res = client.get(f"/api/v1/social/followers/{normal_user.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1

    def test_list_following(self, client, db, admin_user, normal_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post(f"/api/v1/social/follow/{normal_user.id}", headers=headers)

        res = client.get(f"/api/v1/social/following/{admin_user.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1


class TestUserProfile:
    """用户主页测试 - 公开资料/博客/动态"""

    def test_get_user_profile(self, client, admin_user):
        res = client.get(f"/api/v1/user/{admin_user.id}")
        assert res.status_code == 200
        data = res.json()
        assert data["username"] == "admin"
        assert "level" in data
        assert "followers_count" in data

    def test_get_user_blogs(self, client, admin_user):
        res = client.get(f"/api/v1/user/{admin_user.id}/blogs")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data

    def test_get_user_projects(self, client, admin_user):
        res = client.get(f"/api/v1/user/{admin_user.id}/projects")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data

    def test_get_user_moments(self, client, admin_user, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/v1/moment/", json={"content": "Profile moment", "is_public": True}, headers=headers)

        res = client.get(f"/api/v1/user/{admin_user.id}/moments")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] >= 1

    def test_get_nonexistent_user(self, client):
        res = client.get("/api/v1/user/99999")
        assert res.status_code == 404


class TestPointService:
    """积分服务单元测试"""

    def test_get_level(self):
        from app.services.point_service import point_service
        assert point_service.get_level(0) == 1
        assert point_service.get_level(100) == 2
        assert point_service.get_level(300) == 3
        assert point_service.get_level(50000) == 10

    def test_get_level_title(self):
        from app.services.point_service import point_service
        assert point_service.get_level_title(1) == "新手上路"
        assert point_service.get_level_title(10) == "至尊王者"
        assert point_service.get_level_title(999) == "管理员"

    def test_get_level_progress(self):
        from app.services.point_service import point_service
        progress = point_service.get_level_progress(50)
        assert progress["level"] == 1
        assert progress["progress"] >= 0

    def test_check_daily_limit(self, db, admin_user):
        from app.services.point_service import point_service
        result = point_service.check_daily_limit(db, admin_user.id, "daily_login")
        assert result is True

    def test_award_points_admin_skip(self, db, admin_user):
        from app.services.point_service import point_service
        result = point_service.award_points(db, admin_user.id, "daily_login")
        assert result is None

    def test_award_points_normal_user(self, db, normal_user):
        from app.services.point_service import point_service
        result = point_service.award_points(db, normal_user.id, "daily_login")
        assert result is not None
        assert result["points_change"] == 5

    def test_deduct_points(self, db, normal_user):
        from app.services.point_service import point_service
        result = point_service.deduct_points(db, normal_user.id, "content_deleted")
        assert result is not None
        assert result["points_change"] == -20
