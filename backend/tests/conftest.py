import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base, get_db
from app.main import app
from app.core.security import create_access_token, get_password_hash
from app.models.user_company import (
    User,
    Company,
    Membership,
    RoleEnum,
    CompanyProfile,
    CompanyBrand,
)

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def setup_tenants(db_session):
    # Company A (Owner A)
    user_a = User(
        email="owner_a@companya.com",
        full_name="Owner A",
        hashed_password=get_password_hash("password123"),
        is_active=True,
    )
    db_session.add(user_a)
    await db_session.flush()

    company_a = Company(name="Company A Corp", slug="company-a", is_active=True)
    db_session.add(company_a)
    await db_session.flush()

    mem_a = Membership(company_id=company_a.id, user_id=user_a.id, role=RoleEnum.OWNER)
    db_session.add(mem_a)
    db_session.add(CompanyProfile(company_id=company_a.id))
    db_session.add(CompanyBrand(company_id=company_a.id))

    # Company B (Owner B)
    user_b = User(
        email="owner_b@companyb.com",
        full_name="Owner B",
        hashed_password=get_password_hash("password123"),
        is_active=True,
    )
    db_session.add(user_b)
    await db_session.flush()

    company_b = Company(name="Company B Corp", slug="company-b", is_active=True)
    db_session.add(company_b)
    await db_session.flush()

    mem_b = Membership(company_id=company_b.id, user_id=user_b.id, role=RoleEnum.OWNER)
    db_session.add(mem_b)
    db_session.add(CompanyProfile(company_id=company_b.id))
    db_session.add(CompanyBrand(company_id=company_b.id))

    # Company A Viewer
    viewer_user = User(
        email="viewer@companya.com",
        full_name="Viewer A",
        hashed_password=get_password_hash("password123"),
        is_active=True,
    )
    db_session.add(viewer_user)
    await db_session.flush()

    mem_viewer = Membership(company_id=company_a.id, user_id=viewer_user.id, role=RoleEnum.VIEWER)
    db_session.add(mem_viewer)

    # Company A Member
    member_user = User(
        email="member@companya.com",
        full_name="Member A",
        hashed_password=get_password_hash("password123"),
        is_active=True,
    )
    db_session.add(member_user)
    await db_session.flush()

    mem_member = Membership(company_id=company_a.id, user_id=member_user.id, role=RoleEnum.MEMBER)
    db_session.add(mem_member)

    await db_session.commit()

    token_a = create_access_token({"sub": user_a.id, "company_id": company_a.id, "role": RoleEnum.OWNER.value})
    token_b = create_access_token({"sub": user_b.id, "company_id": company_b.id, "role": RoleEnum.OWNER.value})
    token_viewer = create_access_token({"sub": viewer_user.id, "company_id": company_a.id, "role": RoleEnum.VIEWER.value})
    token_member = create_access_token({"sub": member_user.id, "company_id": company_a.id, "role": RoleEnum.MEMBER.value})

    return {
        "company_a": company_a,
        "company_b": company_b,
        "user_a": user_a,
        "user_b": user_b,
        "viewer_user": viewer_user,
        "member_user": member_user,
        "headers_a": {"Authorization": f"Bearer {token_a}"},
        "headers_b": {"Authorization": f"Bearer {token_b}"},
        "headers_viewer": {"Authorization": f"Bearer {token_viewer}"},
        "headers_member": {"Authorization": f"Bearer {token_member}"},
    }
