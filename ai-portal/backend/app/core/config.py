"""
全局配置模块 - 使用pydantic-settings从环境变量/.env文件加载所有配置
所有配置项均支持环境变量覆盖，优先级：环境变量 > .env文件 > 默认值
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用全局配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==================== 应用基础配置 ====================
    APP_NAME: str = "AI技术门户"
    """应用名称"""
    APP_VERSION: str = "1.0.0"
    """应用版本号"""
    DEBUG: bool = False
    """调试模式（生产环境必须为False）"""
    LOG_LEVEL: str = "DEBUG"
    """日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL），可通过.env配置"""
    SECRET_KEY: str = "change-me-in-production-use-a-strong-random-key"
    """JWT签名密钥（生产环境必须更换为强随机密钥）"""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    """访问令牌过期时间（分钟），默认30分钟"""
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    """刷新令牌过期时间（天），默认30天"""
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    """CORS允许的来源，多个用逗号分隔"""

    # ==================== 数据库配置 ====================
    DATABASE_URL: str = "sqlite:///./ai_portal.db"
    """数据库连接URL，SQLite使用相对路径"""

    # ==================== 大模型配置 - DeepSeek ====================
    DEEPSEEK_API_KEY: str = ""
    """DeepSeek API密钥"""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    """DeepSeek API基础URL"""

    # ==================== 大模型配置 - GLM（智谱AI） ====================
    GLM_API_KEY: str = ""
    """智谱AI API密钥"""
    GLM_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    """智谱AI API基础URL"""

    # ==================== 大模型配置 - Qwen（通义千问） ====================
    QWEN_API_KEY: str = ""
    """通义千问API密钥"""
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    """通义千问API基础URL"""

    # ==================== 大模型配置 - Doubao（豆包/火山引擎） ====================
    DOUBAO_API_KEY: str = ""
    """豆包API密钥"""
    DOUBAO_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    """豆包API基础URL"""

    # ==================== 聊天限制配置 ====================
    DAILY_CHAT_LIMIT: int = 50
    """每日聊天次数限制"""
    MAX_TOKENS_PER_REQUEST: int = 4096
    """单次请求最大Token数"""
    DEFAULT_MODEL: str = "deepseek-chat"
    """默认聊天模型"""

    # ==================== RAG配置 ====================
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    """ChromaDB持久化目录"""
    EMBEDDING_DIMENSION: int = 384
    """向量嵌入维度（需与sentence-transformers模型匹配）"""
    CHUNK_SIZE: int = 500
    """文档分块大小（字符数）"""
    CHUNK_OVERLAP: int = 50
    """文档分块重叠大小（字符数）"""

    # ==================== 文件上传配置 ====================
    UPLOAD_DIR: str = "./uploads"
    """上传文件存储目录"""
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    """最大上传文件大小（字节），默认50MB"""

    # ==================== 备份配置 ====================
    BACKUP_DIR: str = "./backups"
    """备份文件存储目录"""
    BACKUP_RETENTION_DAYS: int = 30
    """备份保留天数"""

    # ==================== 认证配置 ====================
    REMEMBER_ME_DAYS: int = 30
    """记住我功能的有效天数"""

    # ==================== 管理员默认账号 ====================
    ADMIN_USERNAME: str = "admin"
    """管理员默认用户名"""
    ADMIN_PASSWORD: str = "admin123"
    """管理员默认密码（首次启动后请立即修改）"""
    ADMIN_EMAIL: str = "admin@aiportal.local"
    """管理员默认邮箱"""

    def get_allowed_origins_list(self) -> list[str]:
        """将ALLOWED_ORIGINS字符串解析为列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


# 全局配置单例
settings = Settings()
