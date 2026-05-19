"""
模拟真人用户操作集成测试
覆盖：注册→登录→改资料→上传头像→发帖→图片上传→作者主页→关注→私信→通知
"""
import io
import pytest
from app.models import User


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestUserRegistrationAndLogin:
    """模拟用户注册和登录流程"""

    def test_register_new_user(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "TestPass123!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"
        assert data["level"] == 1

    def test_register_duplicate_username(self, client, normal_user):
        resp = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "another@test.com",
            "password": "TestPass123!",
        })
        assert resp.status_code in (400, 409)

    def test_login_success(self, client, normal_user):
        resp = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, normal_user):
        resp = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword",
        })
        assert resp.status_code in (401, 400)

    def test_full_register_then_login_flow(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "username": "flowuser",
            "email": "flow@test.com",
            "password": "FlowPass123!",
        })
        assert resp.status_code == 200

        resp = client.post("/api/v1/auth/login", json={
            "username": "flowuser",
            "password": "FlowPass123!",
        })
        assert resp.status_code == 200
        token = resp.json()["access_token"]

        resp = client.get("/api/v1/auth/me", headers=_auth(token))
        assert resp.status_code == 200
        assert resp.json()["username"] == "flowuser"


class TestProfileManagement:
    """模拟用户修改个人资料流程"""

    def test_get_profile(self, client, user_token):
        resp = client.get("/api/v1/auth/profile", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "username" in data
        assert "avatar_url" in data
        assert "nickname" in data
        assert "bio" in data
        assert "level" in data
        assert "points" in data
        assert "followers_count" in data
        assert "following_count" in data

    def test_update_nickname_and_bio(self, client, user_token):
        resp = client.put("/api/v1/auth/profile", headers=_auth(user_token), json={
            "nickname": "测试昵称",
            "bio": "这是我的个人简介",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["nickname"] == "测试昵称"
        assert data["bio"] == "这是我的个人简介"

    def test_update_avatar_url(self, client, user_token):
        resp = client.put("/api/v1/auth/profile", headers=_auth(user_token), json={
            "avatar_url": "/uploads/avatar/test_avatar.png",
        })
        assert resp.status_code == 200
        assert resp.json()["avatar_url"] == "/uploads/avatar/test_avatar.png"

    def test_update_all_profile_fields(self, client, user_token):
        resp = client.put("/api/v1/auth/profile", headers=_auth(user_token), json={
            "nickname": "全量更新",
            "bio": "全量更新简介",
            "avatar_url": "/uploads/avatar/full_update.png",
            "gender": "男",
            "location": "北京",
            "website": "https://example.com",
            "github": "testgithub",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["nickname"] == "全量更新"
        assert data["bio"] == "全量更新简介"
        assert data["avatar_url"] == "/uploads/avatar/full_update.png"
        assert data["gender"] == "男"
        assert data["location"] == "北京"
        assert data["website"] == "https://example.com"
        assert data["github"] == "testgithub"

    def test_profile_persists_after_refetch(self, client, user_token):
        client.put("/api/v1/auth/profile", headers=_auth(user_token), json={
            "nickname": "持久化测试",
            "avatar_url": "/uploads/avatar/persist.png",
        })

        resp = client.get("/api/v1/auth/profile", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["nickname"] == "持久化测试"
        assert data["avatar_url"] == "/uploads/avatar/persist.png"

    def test_change_password(self, client, normal_user, user_token):
        resp = client.put("/api/v1/auth/password", headers=_auth(user_token), json={
            "old_password": "testpass123",
            "new_password": "NewPass456!",
        })
        assert resp.status_code == 200

        resp = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "NewPass456!",
        })
        assert resp.status_code == 200

    def test_change_password_wrong_old(self, client, user_token):
        resp = client.put("/api/v1/auth/password", headers=_auth(user_token), json={
            "old_password": "wrongold",
            "new_password": "NewPass456!",
        })
        assert resp.status_code in (400, 401)


class TestAvatarUpload:
    """模拟头像上传流程"""

    def test_upload_avatar(self, client, user_token):
        img = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        resp = client.post(
            "/api/v1/auth/avatar",
            headers=_auth(user_token),
            files={"file": ("avatar.png", img, "image/png")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "avatar_url" in data
        assert "/uploads/avatars/" in data["avatar_url"]

    def test_upload_avatar_invalid_type(self, client, user_token):
        txt = io.BytesIO(b"not an image")
        resp = client.post(
            "/api/v1/auth/avatar",
            headers=_auth(user_token),
            files={"file": ("file.txt", txt, "text/plain")},
        )
        assert resp.status_code in (400, 422)

    def test_avatar_upload_updates_profile(self, client, user_token):
        img = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        resp = client.post(
            "/api/v1/auth/avatar",
            headers=_auth(user_token),
            files={"file": ("myavatar.png", img, "image/png")},
        )
        avatar_url = resp.json()["avatar_url"]

        resp = client.get("/api/v1/auth/profile", headers=_auth(user_token))
        assert resp.status_code == 200
        assert resp.json()["avatar_url"] == avatar_url


class TestContentCreationWithImage:
    """模拟发帖+图片上传流程"""

    def test_upload_image_for_blog(self, client, admin_token):
        img = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        resp = client.post(
            "/api/v1/upload/image",
            headers=_auth(admin_token),
            files={"file": ("screenshot.png", img, "image/png")},
            data={"module": "blog"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "url" in data
        assert "/uploads/blog/" in data["url"]

    def test_upload_image_avatar_module(self, client, admin_token):
        img = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        resp = client.post(
            "/api/v1/upload/image",
            headers=_auth(admin_token),
            files={"file": ("face.png", img, "image/png")},
            data={"module": "avatar"},
        )
        assert resp.status_code == 200
        assert "/uploads/avatar/" in resp.json()["url"]

    def test_upload_image_unsafe_module_goes_misc(self, client, admin_token):
        img = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        resp = client.post(
            "/api/v1/upload/image",
            headers=_auth(admin_token),
            files={"file": ("img.png", img, "image/png")},
            data={"module": "hack"},
        )
        assert resp.status_code == 200
        url = resp.json()["url"]
        assert "/uploads/misc/" in url or "/uploads/" in url

    def test_create_blog_with_image_in_content(self, client, admin_token):
        img = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        upload_resp = client.post(
            "/api/v1/upload/image",
            headers=_auth(admin_token),
            files={"file": ("diagram.png", img, "image/png")},
            data={"module": "blog"},
        )
        image_url = upload_resp.json()["url"]

        resp = client.post("/api/v1/blog/posts", headers=_auth(admin_token), json={
            "title": "带图片的博客",
            "content": f"这是一篇带图片的博客\n\n![图片]({image_url})\n\n正文内容",
            "category": "技术",
            "is_published": True,
        })
        assert resp.status_code == 200
        blog = resp.json()
        assert image_url in blog["content"]

    def test_create_news_product_solution_project(self, client, admin_token):
        for module, payload in [
            ("news", {"title": "测试新闻", "content": "新闻内容", "category": "行业", "is_published": True}),
            ("products", {"title": "测试产品", "content": "产品内容", "category": "AI工具", "is_published": True}),
            ("solutions", {"title": "测试方案", "content": "方案内容", "category": "企业", "is_published": True}),
        ]:
            resp = client.post(f"/api/v1/{module}/", headers=_auth(admin_token), json=payload)
            assert resp.status_code in (200, 201), f"Failed to create {module}: {resp.text}"

        resp = client.post("/api/v1/portfolio/projects", headers=_auth(admin_token), json={
            "title": "测试项目", "content": "项目内容", "description": "项目描述", "category": "开源", "is_published": True,
        })
        assert resp.status_code in (200, 201)


class TestAuthorProfileNavigation:
    """模拟点击作者头像/用户名跳转到用户主页"""

    def test_blog_detail_has_author_info(self, client, admin_token, admin_user):
        resp = client.post("/api/v1/blog/posts", headers=_auth(admin_token), json={
            "title": "作者测试博客", "content": "内容", "is_published": True,
        })
        blog_id = resp.json()["id"]

        resp = client.get(f"/api/v1/blog/posts/{blog_id}")
        assert resp.status_code == 200
        blog = resp.json()
        assert "author" in blog
        assert blog["author"]["id"] == admin_user.id

    def test_view_author_public_profile(self, client, admin_user, user_token):
        resp = client.get(f"/api/v1/user/{admin_user.id}", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "admin"
        assert "level" in data
        assert "followers_count" in data
        assert "following_count" in data
        assert "is_following" in data
        assert "is_followed_by" in data
        assert "is_mutual" in data

    def test_view_own_profile_shows_self(self, client, admin_user, admin_token):
        resp = client.get(f"/api/v1/user/{admin_user.id}", headers=_auth(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == admin_user.id

    def test_view_nonexistent_user(self, client, user_token):
        resp = client.get("/api/v1/user/99999", headers=_auth(user_token))
        assert resp.status_code == 404

    def test_author_blogs_list(self, client, admin_token, admin_user):
        for i in range(3):
            client.post("/api/v1/blog/posts", headers=_auth(admin_token), json={
                "title": f"博客{i}", "content": f"内容{i}", "is_published": True,
            })

        resp = client.get(f"/api/v1/user/{admin_user.id}/blogs")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 3
        assert len(data["items"]) >= 3

    def test_author_projects_list(self, client, admin_token, admin_user):
        client.post("/api/v1/portfolio/projects", headers=_auth(admin_token), json={
            "title": "测试项目", "content": "项目内容", "description": "描述", "category": "开源", "is_published": True,
        })

        resp = client.get(f"/api/v1/user/{admin_user.id}/projects")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1


class TestFollowSystem:
    """模拟关注/取关流程"""

    def test_follow_user(self, client, admin_user, normal_user, user_token):
        resp = client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_following"] is True
        assert data["followers_count"] >= 1

    def test_unfollow_user(self, client, admin_user, user_token):
        client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))

        resp = client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_following"] is False

    def test_cannot_follow_self(self, client, user_token, normal_user):
        resp = client.post(f"/api/v1/social/follow/{normal_user.id}", headers=_auth(user_token))
        assert resp.status_code in (400, 403)

    def test_follow_status(self, client, admin_user, user_token):
        client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))

        resp = client.get(f"/api/v1/social/follow-status/{admin_user.id}", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_following"] is True
        assert data["is_followed_by"] is False
        assert data["is_mutual"] is False

    def test_mutual_follow(self, client, admin_user, admin_token, normal_user, user_token):
        client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))
        client.post(f"/api/v1/social/follow/{normal_user.id}", headers=_auth(admin_token))

        resp = client.get(f"/api/v1/social/follow-status/{admin_user.id}", headers=_auth(user_token))
        data = resp.json()
        assert data["is_following"] is True
        assert data["is_followed_by"] is True
        assert data["is_mutual"] is True

    def test_followers_list(self, client, admin_user, user_token):
        client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))

        resp = client.get(f"/api/v1/social/followers/{admin_user.id}", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_following_list(self, client, admin_user, normal_user, user_token):
        client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))

        resp = client.get(f"/api/v1/social/following/{normal_user.id}", headers=_auth(user_token))
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_follow_updates_profile_counts(self, client, admin_user, user_token):
        resp_before = client.get(f"/api/v1/user/{admin_user.id}", headers=_auth(user_token))
        followers_before = resp_before.json()["followers_count"]

        client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))

        resp_after = client.get(f"/api/v1/user/{admin_user.id}", headers=_auth(user_token))
        assert resp_after.json()["followers_count"] == followers_before + 1


class TestDirectMessaging:
    """模拟私信流程"""

    def test_send_message(self, client, admin_user, user_token):
        resp = client.post("/api/v1/message/send", headers=_auth(user_token), json={
            "receiver_id": admin_user.id,
            "content": "你好，管理员！",
        })
        assert resp.status_code == 200
        assert "id" in resp.json()

    def test_cannot_message_self(self, client, normal_user, user_token):
        resp = client.post("/api/v1/message/send", headers=_auth(user_token), json={
            "receiver_id": normal_user.id,
            "content": "自言自语",
        })
        assert resp.status_code in (400, 403)

    def test_conversations_list(self, client, admin_user, user_token):
        client.post("/api/v1/message/send", headers=_auth(user_token), json={
            "receiver_id": admin_user.id,
            "content": "第一条私信",
        })

        resp = client.get("/api/v1/message/conversations", headers=_auth(user_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        conv = data["items"][0]
        assert "relationship" in conv
        assert "unread_count" in conv
        assert "last_message" in conv

    def test_conversation_messages(self, client, admin_user, user_token):
        client.post("/api/v1/message/send", headers=_auth(user_token), json={
            "receiver_id": admin_user.id,
            "content": "消息1",
        })
        client.post("/api/v1/message/send", headers=_auth(user_token), json={
            "receiver_id": admin_user.id,
            "content": "消息2",
        })

        resp = client.get(f"/api/v1/message/conversations/{admin_user.id}", headers=_auth(user_token))
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) >= 2
        assert messages[0]["content"] == "消息1"
        assert messages[1]["content"] == "消息2"

    def test_unread_count(self, client, admin_user, admin_token, user_token):
        client.post("/api/v1/message/send", headers=_auth(user_token), json={
            "receiver_id": admin_user.id,
            "content": "未读测试",
        })

        resp = client.get("/api/v1/message/unread-count", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["unread_count"] >= 1

    def test_mark_messages_read(self, client, admin_user, admin_token, normal_user, user_token):
        client.post("/api/v1/message/send", headers=_auth(user_token), json={
            "receiver_id": admin_user.id,
            "content": "标记已读测试",
        })

        resp = client.put(f"/api/v1/message/read/{normal_user.id}", headers=_auth(admin_token))
        assert resp.status_code == 200

    def test_message_relationship_label(self, client, admin_user, user_token):
        client.post("/api/v1/message/send", headers=_auth(user_token), json={
            "receiver_id": admin_user.id,
            "content": "关系标签测试",
        })

        resp = client.get("/api/v1/message/conversations", headers=_auth(user_token))
        conv = resp.json()["items"][0]
        assert conv["relationship"] in ("陌生人", "我关注的人", "关注你的人", "互相关注")


class TestNotificationSystem:
    """模拟通知流程"""

    def test_follow_creates_notification(self, client, admin_user, admin_token, user_token):
        client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))

        resp = client.get("/api/v1/notification", headers=_auth(admin_token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert any(n["type"] == "follow" for n in data["items"])

    def test_like_creates_notification(self, client, admin_token, user_token):
        blog_resp = client.post("/api/v1/blog/posts", headers=_auth(admin_token), json={
            "title": "点赞通知测试", "content": "内容", "is_published": True,
        })
        blog_id = blog_resp.json()["id"]

        client.post(f"/api/v1/interaction/like/blog/{blog_id}", headers=_auth(user_token))

        resp = client.get("/api/v1/notification", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert any(n["type"] == "like" for n in resp.json()["items"])

    def test_comment_creates_notification(self, client, admin_token, user_token):
        blog_resp = client.post("/api/v1/blog/posts", headers=_auth(admin_token), json={
            "title": "评论通知测试", "content": "内容", "is_published": True,
        })
        blog_id = blog_resp.json()["id"]

        resp = client.post(f"/api/v1/comments/blog/{blog_id}", headers=_auth(user_token), json={
            "content": "好文章！",
        })
        assert resp.status_code == 200
        assert resp.json()["content"] == "好文章！"

    def test_notification_unread_count(self, client, admin_user, user_token, admin_token):
        client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))

        resp = client.get("/api/v1/notification/unread-count", headers=_auth(admin_token))
        assert resp.status_code == 200
        assert resp.json()["unread_count"] >= 1

    def test_mark_notification_read(self, client, admin_user, user_token, admin_token):
        client.post(f"/api/v1/social/follow/{admin_user.id}", headers=_auth(user_token))

        notif_resp = client.get("/api/v1/notification", headers=_auth(admin_token))
        notif_id = notif_resp.json()["items"][0]["id"]

        resp = client.put(f"/api/v1/notification/{notif_id}/read", headers=_auth(admin_token))
        assert resp.status_code == 200


class TestEndToEndUserJourney:
    """端到端用户旅程：注册→完善资料→发帖→被关注→收私信→查看通知"""

    def test_full_user_journey(self, client, admin_user, admin_token):
        reg_resp = client.post("/api/v1/auth/register", json={
            "username": "journey_user",
            "email": "journey@test.com",
            "password": "Journey123!",
        })
        assert reg_resp.status_code == 200

        login_resp = client.post("/api/v1/auth/login", json={
            "username": "journey_user",
            "password": "Journey123!",
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = _auth(token)

        profile_resp = client.get("/api/v1/auth/profile", headers=headers)
        assert profile_resp.status_code == 200
        assert profile_resp.json()["nickname"] is None

        update_resp = client.put("/api/v1/auth/profile", headers=headers, json={
            "nickname": "旅途用户",
            "bio": "我是一名AI爱好者",
            "gender": "保密",
            "location": "上海",
        })
        assert update_resp.status_code == 200
        assert update_resp.json()["nickname"] == "旅途用户"

        img = io.BytesIO(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
        avatar_resp = client.post(
            "/api/v1/auth/avatar",
            headers=headers,
            files={"file": ("face.png", img, "image/png")},
        )
        assert avatar_resp.status_code == 200
        avatar_url = avatar_resp.json()["avatar_url"]

        profile_resp2 = client.get("/api/v1/auth/profile", headers=headers)
        assert profile_resp2.json()["avatar_url"] == avatar_url

        me_resp = client.get("/api/v1/auth/me", headers=headers)
        my_id = me_resp.json()["id"]

        follow_resp = client.post(f"/api/v1/social/follow/{my_id}", headers=_auth(admin_token))
        assert follow_resp.status_code == 200
        assert follow_resp.json()["is_following"] is True

        profile_resp3 = client.get("/api/v1/auth/profile", headers=headers)
        assert profile_resp3.json()["followers_count"] >= 1

        msg_resp = client.post("/api/v1/message/send", headers=_auth(admin_token), json={
            "receiver_id": my_id,
            "content": "欢迎加入AI Portal！",
        })
        assert msg_resp.status_code == 200

        conv_resp = client.get("/api/v1/message/conversations", headers=headers)
        assert conv_resp.status_code == 200
        assert conv_resp.json()["total"] >= 1

        notif_resp = client.get("/api/v1/notification", headers=headers)
        assert notif_resp.status_code == 200
        assert notif_resp.json()["total"] >= 1

        admin_profile_resp = client.get(f"/api/v1/user/{admin_user.id}", headers=headers)
        assert admin_profile_resp.status_code == 200
        assert admin_profile_resp.json()["username"] == "admin"

        user_blogs_resp = client.get(f"/api/v1/user/{my_id}/blogs")
        assert user_blogs_resp.status_code == 200
