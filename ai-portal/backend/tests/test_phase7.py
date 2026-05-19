"""
Phase 7 自动化测试 - 成就系统 + 签到系统
"""
import pytest
from datetime import date, timedelta
from app.core.security import create_access_token, get_password_hash
from app.models import User, Blog, Achievement, UserAchievement
from app.models.checkin import CheckinRecord
from app.services.achievement_service import achievement_service, ACHIEVEMENT_SEEDS


class TestAchievementModule:
    """成就模块测试"""

    def test_achievement_seeds_defined(self):
        assert len(ACHIEVEMENT_SEEDS) == 20

    def test_seed_achievements(self, db):
        achievement_service.seed_achievements(db)
        count = db.query(Achievement).count()
        assert count == 20

    def test_seed_idempotent(self, db):
        achievement_service.seed_achievements(db)
        achievement_service.seed_achievements(db)
        count = db.query(Achievement).count()
        assert count == 20

    def test_list_achievements_api(self, client, db, admin_user, admin_token):
        achievement_service.seed_achievements(db)
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/v1/achievement/", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 20
        assert "items" in data
        assert "unlocked_count" in data

    def test_get_achievement_by_code(self, client, db, admin_user, admin_token):
        achievement_service.seed_achievements(db)
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/v1/achievement/first_blog", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["code"] == "first_blog"
        assert data["name"] == "初出茅庐"

    def test_check_achievements_after_blog(self, client, db, admin_user, admin_token):
        achievement_service.seed_achievements(db)
        headers = {"Authorization": f"Bearer {admin_token}"}
        client.post("/api/v1/blog/posts", json={
            "title": "Achievement Test",
            "content": "c",
            "category": "技术",
            "is_published": True,
        }, headers=headers)

        res = client.post("/api/v1/achievement/check", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["newly_unlocked"] >= 1

    def test_secret_achievement_hidden(self, client, db, admin_user, admin_token):
        achievement_service.seed_achievements(db)
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/v1/achievement/", headers=headers)
        data = res.json()
        for item in data["items"]:
            if item["is_secret"] and not item["is_unlocked"]:
                assert item["name"] == "???"
                assert item["icon"] == "🔒"

    def test_achievement_not_found(self, client, db, admin_user, admin_token):
        achievement_service.seed_achievements(db)
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/api/v1/achievement/nonexistent_code", headers=headers)
        assert res.status_code == 404

    def test_achievement_tier_types(self, db):
        achievement_service.seed_achievements(db)
        tiers = set()
        for ach in db.query(Achievement).all():
            tiers.add(ach.tier)
        assert "bronze" in tiers
        assert "silver" in tiers
        assert "gold" in tiers
        assert "diamond" in tiers

    def test_achievement_categories(self, db):
        achievement_service.seed_achievements(db)
        categories = set()
        for ach in db.query(Achievement).all():
            categories.add(ach.category)
        assert "content" in categories
        assert "social" in categories


class TestCheckinModule:
    """签到模块测试"""

    def test_do_checkin(self, client, db, normal_user, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        res = client.post("/api/v1/checkin/", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["points_awarded"] >= 5
        assert data["continuous_days"] >= 1

    def test_double_checkin(self, client, db, normal_user, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        client.post("/api/v1/checkin/", headers=headers)
        res = client.post("/api/v1/checkin/", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is False

    def test_checkin_status_after_checkin(self, client, db, normal_user, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        client.post("/api/v1/checkin/", headers=headers)
        res = client.get("/api/v1/checkin/status", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["is_checked_in"] is True

    def test_checkin_status_not_checked(self, client, db, normal_user, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        res = client.get("/api/v1/checkin/status", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["is_checked_in"] is False

    def test_checkin_calendar(self, client, db, normal_user, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        client.post("/api/v1/checkin/", headers=headers)
        today = date.today()
        res = client.get("/api/v1/checkin/calendar", params={"year": today.year, "month": today.month}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["year"] == today.year
        assert len(data["days"]) > 0

    def test_checkin_ranking(self, client, db, normal_user, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        client.post("/api/v1/checkin/", headers=headers)
        res = client.get("/api/v1/checkin/ranking")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data

    def test_checkin_creates_record(self, client, db, normal_user, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        res = client.post("/api/v1/checkin/", headers=headers)
        assert res.status_code == 200
        assert res.json()["success"] is True


class TestAchievementService:
    """成就服务单元测试"""

    def test_get_progress_blog(self, db, normal_user):
        achievement_service.seed_achievements(db)
        db.add(Blog(title="t1", content="c", author_id=normal_user.id, is_published=True))
        db.add(Blog(title="t2", content="c", author_id=normal_user.id, is_published=True))
        db.commit()

        ach = db.query(Achievement).filter(Achievement.code == "first_blog").first()
        progress = achievement_service._get_progress(db, normal_user.id, ach)
        assert progress == 2

    def test_check_all_unlocks_achievement(self, db, normal_user):
        achievement_service.seed_achievements(db)
        db.add(Blog(title="t1", content="c", author_id=normal_user.id, is_published=True))
        db.commit()

        newly = achievement_service.check_all(db, normal_user.id)
        codes = [a["code"] for a in newly]
        assert "first_blog" in codes

    def test_check_all_no_duplicate_unlock(self, db, normal_user):
        achievement_service.seed_achievements(db)
        db.add(Blog(title="t1", content="c", author_id=normal_user.id, is_published=True))
        db.commit()

        achievement_service.check_all(db, normal_user.id)
        newly = achievement_service.check_all(db, normal_user.id)
        codes = [a["code"] for a in newly]
        assert "first_blog" not in codes
