"""Phase 8 测试 - Recommend + Feed 模块"""
import pytest
from app.models import Blog, News, Product, Moment, UserFollow


@pytest.fixture
def seed_content(client, db, admin_user, normal_user):
    blog = Blog(
        title="推荐测试博客",
        content="这是一篇用于测试推荐算法的博客内容",
        summary="推荐测试博客摘要",
        category="AI",
        tags="推荐,测试,算法",
        author_id=admin_user.id,
        is_published=True,
        view_count=100,
        likes_count=50,
    )
    db.add(blog)

    news = News(
        title="推荐测试新闻",
        content="这是一条用于测试推荐算法的新闻内容",
        summary="推荐测试新闻摘要",
        category="科技",
        tags="新闻,推荐",
        author_id=admin_user.id,
        is_published=True,
        view_count=200,
    )
    db.add(news)

    product = Product(
        title="推荐测试产品",
        content="这是一个用于测试推荐算法的产品内容",
        summary="推荐测试产品摘要",
        category="工具",
        tags="产品,AI",
        author_id=admin_user.id,
        is_published=True,
        view_count=50,
    )
    db.add(product)

    moment = Moment(
        content="测试动态内容用于Feed流",
        user_id=normal_user.id,
        likes_count=5,
    )
    db.add(moment)
    db.commit()

    return {"blog": blog, "news": news, "product": product, "moment": moment}


class TestRecommendModule:
    def test_recommend_feed(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/feed", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_recommend_feed_pagination(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/feed?page=1&page_size=2", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) <= 2

    def test_recommend_feed_no_auth(self, client, seed_content):
        res = client.get("/api/v1/recommend/feed")
        assert res.status_code == 200

    def test_recommend_hot(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/hot", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data

    def test_recommend_hot_sorted_by_score(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/hot", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        if len(data["items"]) >= 2:
            for i in range(len(data["items"]) - 1):
                assert data["items"][i]["score"] >= data["items"][i + 1]["score"]

    def test_recommend_related_blog(self, client, admin_token, seed_content):
        blog_id = seed_content["blog"].id
        res = client.get(f"/api/v1/recommend/related/blog/{blog_id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert "items" in data

    def test_recommend_related_invalid_type(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/related/invalid/999", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["items"] == []

    def test_recommend_related_nonexistent_id(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/related/blog/99999", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["items"] == []

    def test_trending_tags(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/trending-tags", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert "tags" in data
        assert isinstance(data["tags"], list)

    def test_trending_tags_with_limit(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/trending-tags?limit=5", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["tags"]) <= 5

    def test_recommend_item_structure(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/feed", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        if data["items"]:
            item = data["items"][0]
            assert "id" in item
            assert "title" in item
            assert "content_type" in item
            assert "score" in item
            assert "view_count" in item
            assert "likes_count" in item


class TestFeedModule:
    def test_feed_all(self, client, admin_token, seed_content):
        res = client.get("/api/v1/feed/all", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    def test_feed_all_pagination(self, client, admin_token, seed_content):
        res = client.get("/api/v1/feed/all?page=1&page_size=2", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) <= 2

    def test_feed_following_requires_auth(self, client, seed_content):
        res = client.get("/api/v1/feed/")
        assert res.status_code == 401

    def test_feed_following_empty(self, client, user_token, seed_content):
        res = client.get("/api/v1/feed/", headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_feed_following_with_follow(self, client, db, user_token, admin_user, normal_user, seed_content):
        follow = UserFollow(follower_id=normal_user.id, following_id=admin_user.id)
        db.add(follow)
        db.commit()

        res = client.get("/api/v1/feed/", headers={"Authorization": f"Bearer {user_token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] > 0

    def test_feed_item_structure(self, client, admin_token, seed_content):
        res = client.get("/api/v1/feed/all", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        if data["items"]:
            item = data["items"][0]
            assert "id" in item
            assert "content_type" in item
            assert "author_name" in item
            assert "created_at" in item

    def test_feed_all_contains_content(self, client, admin_token, seed_content):
        res = client.get("/api/v1/feed/all", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        content_types = [item["content_type"] for item in data["items"]]
        assert "blog" in content_types or "moment" in content_types


class TestRecommendScoring:
    def test_score_calculation(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/feed", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        for item in data["items"]:
            assert item["score"] >= 0

    def test_hot_content_has_higher_score(self, client, admin_token, seed_content):
        res = client.get("/api/v1/recommend/hot", headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        data = res.json()
        if len(data["items"]) >= 2:
            assert data["items"][0]["score"] >= data["items"][-1]["score"]
