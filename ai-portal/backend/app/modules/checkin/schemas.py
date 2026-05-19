"""签到模块 - 请求/响应模型"""
from pydantic import BaseModel
from datetime import date, datetime


class CheckinResponse(BaseModel):
    success: bool
    message: str
    points_awarded: int
    continuous_days: int
    bonus_points: int = 0


class CheckinStatusResponse(BaseModel):
    is_checked_in: bool
    continuous_days: int
    last_checkin_date: date | None


class CheckinCalendarItem(BaseModel):
    date: date
    is_checked_in: bool


class CheckinCalendarResponse(BaseModel):
    year: int
    month: int
    days: list[CheckinCalendarItem]
    continuous_days: int


class CheckinRankingItem(BaseModel):
    user_id: int
    username: str
    nickname: str | None
    avatar_url: str | None
    continuous_days: int


class CheckinRankingResponse(BaseModel):
    items: list[CheckinRankingItem]
    total: int
