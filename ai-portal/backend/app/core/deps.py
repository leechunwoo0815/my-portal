"""
依赖注入模块 - 提供FastAPI的Depends依赖项
包括数据库会话管理、当前用户获取、管理员权限校验
"""

import logging
from typing import Annotated, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models import User

logger = logging.getLogger("ai-portal.auth")

# OAuth2密码模式令牌获取地址
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    """
    数据库会话依赖项 - 每个请求获取一个独立的数据库会话

    Yields:
        Session: SQLAlchemy数据库会话对象

    注意：
        WAL模式已在database.py的engine connect事件中自动设置，此处无需重复
        请求结束后自动关闭会话，确保连接释放
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    获取当前认证用户 - 从JWT令牌中解析用户身份

    Args:
        token: OAuth2令牌
        db: 数据库会话

    Returns:
        User: 当前认证的用户对象

    Raises:
        HTTPException: 令牌无效或用户不存在时抛出401错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        logger.warning("JWT验证失败: token=%s...", token[:20] if len(token) > 20 else token)
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        logger.warning("JWT缺少sub字段")
        raise credentials_exception

    # 兼容旧token: sub可能是username或user_id
    try:
        user_id_int = int(user_id)
        user = db.query(User).filter(User.id == user_id_int).first()
    except ValueError:
        # 旧token sub存的是username
        user = db.query(User).filter(User.username == user_id).first()
    if user is None:
        logger.warning("用户不存在: id=%s", user_id)
        raise credentials_exception

    if not user.is_active:
        logger.warning("用户已被禁用: id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    return user


def get_optional_current_user(
    token: str | None = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> User | None:
    """可选的当前用户 - 未登录返回 None，已登录返回 User"""
    if token is None:
        return None
    try:
        payload = decode_access_token(token)
        if payload is None:
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        # 兼容旧token: sub可能是username或user_id
        try:
            user_id_int = int(user_id)
            user = db.query(User).filter(User.id == user_id_int).first()
        except ValueError:
            user = db.query(User).filter(User.username == user_id).first()
        if user is None or not user.is_active:
            return None
        return user
    except Exception:
        return None


def require_level(min_level: int):
    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_admin:
            return current_user
        if current_user.level < min_level:
            from app.core.exceptions import PermissionDenied
            raise PermissionDenied(f"需要LV{min_level}或更高权限")
        return current_user
    return _check


def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    管理员权限校验 - 确保当前用户具有管理员角色

    Args:
        current_user: 当前认证用户

    Returns:
        User: 管理员用户对象

    Raises:
        HTTPException: 非管理员用户抛出403错误
    """
    if not current_user.is_admin:
        logger.warning("非管理员访问受限资源: user=%s", current_user.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user


# 常用依赖类型别名，简化路由函数签名
DbDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
AdminUserDep = Annotated[User, Depends(require_admin)]
