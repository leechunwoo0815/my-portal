"""
安全模块 - JWT令牌生成/验证、密码哈希、API Key加密
使用 python-jose + bcrypt + cryptography Fernet
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import base64

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

import logging
logger = logging.getLogger("ai-portal.security")

ALGORITHM = "HS256"

# ============================================================
# Fernet 加密：用于 API Key 的加密存储
# ============================================================
_fernet = None


def _get_fernet():
    """延迟初始化 Fernet（基于 SECRET_KEY 派生 32 字节密钥）"""
    global _fernet
    if _fernet is None:
        from cryptography.fernet import Fernet
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        _fernet = Fernet(base64.urlsafe_b64encode(key))
    return _fernet


def encrypt_api_key(plaintext: str) -> str:
    """加密 API Key，返回 base64 编码的密文"""
    if not plaintext:
        return ""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_api_key(ciphertext: str) -> str:
    """解密 API Key，返回明文"""
    if not ciphertext:
        return ""
    try:
        return _get_fernet().decrypt(ciphertext.encode()).decode()
    except Exception as e:
        logger.error("API Key解密失败: %s", str(e))
        # 兼容旧的明文存储：如果解密失败，认为它本身就是明文
        return ciphertext


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与 bcrypt 哈希密码是否匹配"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error("密码验证失败: %s", str(e))
        return False


def get_password_hash(password: str) -> str:
    """生成密码的 bcrypt 哈希值"""
    raw = password.encode('utf-8')[:72]  # bcrypt 限制 72 字节
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(raw, salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT 访问令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """解码并验证 JWT 访问令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT 刷新令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_refresh_token(token: str) -> Optional[dict]:
    """解码并验证 JWT 刷新令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
