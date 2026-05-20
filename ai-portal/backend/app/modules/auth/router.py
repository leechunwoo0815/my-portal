"""认证API路由 - 登录、注册、获取当前用户、修改密码、个人资料"""
import hashlib
import logging
from datetime import timedelta, timezone, datetime
from typing import Any

from fastapi import APIRouter, Depends, status, File, UploadFile, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.core.exceptions import AuthError, PermissionDenied, AlreadyExists, FileError, FileTooLarge

logger = logging.getLogger("ai-portal.auth")

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_refresh_token
from app.core.deps import get_db, get_current_user
from app.core.events import EventBus
from app.models import User, RefreshToken
from app.modules.auth.schemas import (
    LoginRequest,
    TokenResponse,
    PasswordChangeRequest,
    UserResponse,
    RegisterRequest,
    RegisterResponse,
    UserProfileResponse,
    ProfileUpdateRequest,
    RefreshRequest,
)
from app.services.point_service import point_service, LEVEL_TITLES

router = APIRouter(tags=["认证"])
limiter = Limiter(key_func=get_remote_address)


def _issue_refresh_token(db: Session, user_id: int) -> str:
    """创建并存储 refresh_token，返回 token 字符串"""
    import uuid
    token = create_refresh_token(data={"sub": str(user_id), "jti": uuid.uuid4().hex})
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at))
    db.commit()
    return token


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, login_request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """用户登录"""
    user = db.query(User).filter(User.username == login_request.username).first()
    if not user or not verify_password(login_request.password, user.hashed_password):
        logger.warning("登录失败: 用户名=%s", login_request.username)
        raise AuthError("用户名或密码错误")
    if not user.is_active:
        raise PermissionDenied("用户已被禁用")

    logger.info("用户登录: %s", login_request.username)

    # 每日登录积分
    if point_service.check_daily_limit(db, user.id, "daily_login"):
        point_service.award_points(db, user.id, "daily_login", "每日登录奖励")

    expires_delta = (
        timedelta(days=settings.REMEMBER_ME_DAYS)
        if login_request.remember_me
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=expires_delta,
    )
    refresh_token = _issue_refresh_token(db, user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(expires_delta.total_seconds()),
    )


@router.post("/register", response_model=RegisterResponse)
@limiter.limit("5/minute")
def register(request: Request, register_request: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    """用户注册"""
    existing_user = db.query(User).filter(
        (User.username == register_request.username) | (User.email == register_request.email)
    ).first()
    if existing_user:
        if existing_user.username == register_request.username:
            raise AlreadyExists("用户名")
        raise AlreadyExists("邮箱")

    hashed = get_password_hash(register_request.password)
    new_user = User(
        username=register_request.username,
        email=register_request.email,
        hashed_password=hashed,
        level=1,
        points=0,
        total_points=0,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("新用户注册: %s", register_request.username)

    EventBus.emit_sync("user.registered", new_user)

    return RegisterResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        level=1,
        message="注册成功，请登录",
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: Request, body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """用 refresh_token 换取新的 access_token + refresh_token"""
    payload = decode_refresh_token(body.refresh_token)
    if payload is None:
        raise AuthError("刷新令牌无效或已过期")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthError("刷新令牌格式错误")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise AuthError("刷新令牌格式错误")

    # 验证 refresh_token 在数据库中存在且未被吊销
    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    stored = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked == False,
    ).first()
    if not stored:
        raise AuthError("刷新令牌已失效")

    # 吊销旧的 refresh_token（rotation）
    stored.revoked = True
    db.commit()

    # 验证用户存在且活跃
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AuthError("用户不存在或已被禁用")

    # 签发新的 access_token + refresh_token
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = _issue_refresh_token(db, user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """获取当前登录用户信息"""
    return current_user


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)) -> dict:
    """获取当前用户详细信息"""
    level_title = LEVEL_TITLES.get(current_user.level, "新手上路")
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "nickname": current_user.nickname,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "level": current_user.level,
        "points": current_user.points,
        "total_points": current_user.total_points,
        "followers_count": current_user.followers_count,
        "following_count": current_user.following_count,
        "gender": current_user.gender,
        "location": current_user.location,
        "website": current_user.website,
        "github": current_user.github,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "level_title": level_title,
    }


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """修改个人资料"""
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return get_profile(current_user)


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """上传头像"""
    from pathlib import Path
    import uuid

    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise FileError("只支持 jpg/png/gif/webp 格式")

    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise FileTooLarge(2)

    upload_dir = Path(settings.UPLOAD_DIR) / "avatars"
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = file.filename.split('.')[-1] if '.' in (file.filename or '') else 'jpg'
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = upload_dir / filename

    with open(file_path, "wb") as f:
        f.write(content)

    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    db.commit()

    return {"avatar_url": avatar_url}


@router.put("/password")
def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """修改当前用户密码"""
    if not verify_password(request.old_password, current_user.hashed_password):
        raise AuthError("旧密码错误")
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    logger.info("密码修改: user_id=%s", current_user.id)
    return {"message": "密码修改成功，请重新登录"}
