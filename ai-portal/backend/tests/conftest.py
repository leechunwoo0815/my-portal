"""
Pytest 共享 fixtures：测试数据库、FastAPI client、admin token。
所有测试通过这些 fixtures 操作，确保隔离。
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base
from app.core.deps import get_db
from app.core.security import create_access_token, get_password_hash
from app.models import User

# 测试用 SQLite（内存模式，每个测试隔离）
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 每次连接自动开启 WAL + foreign_keys
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(autouse=True)
def setup_db():
    """每个测试前后自动建表/删表"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """独立的数据库 session"""
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db):
    """带测试数据库的 FastAPI TestClient"""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db):
    """创建测试 admin 用户"""
    user = User(
        username="admin",
        email="test@aiportal.local",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def normal_user(db):
    """创建测试普通用户"""
    user = User(
        username="testuser",
        email="user@aiportal.local",
        hashed_password=get_password_hash("testpass123"),
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    """admin 用户的 JWT token"""
    return create_access_token(data={"sub": str(admin_user.id)})


@pytest.fixture
def user_token(normal_user):
    """普通用户的 JWT token"""
    return create_access_token(data={"sub": str(normal_user.id)})


def auth_header(token):
    """构造 Authorization header"""
    return {"Authorization": f"Bearer {token}"}
