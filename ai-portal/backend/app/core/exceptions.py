"""
统一业务异常体系
所有模块自定义异常继承 AppException，避免错误码冲突
"""

from fastapi import HTTPException, status


class AppException(Exception):
    """业务异常基类"""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def to_http(self) -> HTTPException:
        """转换为 FastAPI HTTPException"""
        return HTTPException(
            status_code=self.status_code,
            detail={"code": self.code, "message": self.message},
        )


# ========== 认证相关异常 ==========
class AuthError(AppException):
    """认证失败"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(code="AUTH_ERROR", message=message, status_code=401)


class PermissionDenied(AppException):
    """权限不足"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(code="PERMISSION_DENIED", message=message, status_code=403)


# ========== 资源相关异常 ==========
class NotFound(AppException):
    """资源不存在"""

    def __init__(self, resource: str = "资源"):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource}不存在",
            status_code=404,
        )


class AlreadyExists(AppException):
    """资源已存在"""

    def __init__(self, resource: str = "资源"):
        super().__init__(
            code="ALREADY_EXISTS",
            message=f"{resource}已存在",
            status_code=409,
        )


# ========== 聊天相关异常 ==========
class ChatLimitExceeded(AppException):
    """今日聊天次数已达上限"""

    def __init__(self, limit: int = 50):
        super().__init__(
            code="CHAT_LIMIT_EXCEEDED",
            message=f"今日调用次数已达上限（{limit}次），请明天再试",
            status_code=429,
        )


class ModelNotAvailable(AppException):
    """模型不可用"""

    def __init__(self, model_id: str = ""):
        super().__init__(
            code="MODEL_NOT_AVAILABLE",
            message=f"模型不可用: {model_id}",
            status_code=400,
        )


# ========== 文件相关异常 ==========
class FileError(AppException):
    """文件处理错误"""

    def __init__(self, message: str = "文件处理失败"):
        super().__init__(code="FILE_ERROR", message=message, status_code=400)


class FileTooLarge(AppException):
    """文件过大"""

    def __init__(self, max_size_mb: int = 50):
        super().__init__(
            code="FILE_TOO_LARGE",
            message=f"文件过大，最大允许{max_size_mb}MB",
            status_code=413,
        )


# ========== RAG相关异常 ==========
class RAGError(AppException):
    """RAG处理错误"""

    def __init__(self, message: str = "检索失败"):
        super().__init__(code="RAG_ERROR", message=message, status_code=500)
