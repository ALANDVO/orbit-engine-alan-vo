import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from httpx import AsyncClient, ASGITransport

# Create a SQLite engine for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class TestBase(DeclarativeBase):
    pass


# Import models and bind to test base
from app.models import Domain, Subject, Concept, ConceptPrerequisite, ChildProfile, ConceptProgress, AuditLog, Base as ModelBase


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.create_all)
    async with test_async_session_maker() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    from app.main import app
    from app.core.database import get_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def setup_domain(db_session):
    domain = Domain(name="test", display_name="Test Domain", is_default=True)
    db_session.add(domain)
    await db_session.flush()

    subject = Subject(domain_id=domain.id, name="math", display_name="Mathematics")
    db_session.add(subject)
    await db_session.flush()

    concept1 = Concept(
        domain_id=domain.id,
        subject_id=subject.id,
        concept_id="counting",
        display_name="Counting",
        description="Count to 10",
        difficulty=1,
        age_min=3,
        age_max=5,
    )
    concept2 = Concept(
        domain_id=domain.id,
        subject_id=subject.id,
        concept_id="addition",
        display_name="Addition",
        description="Add numbers",
        difficulty=2,
        age_min=4,
        age_max=6,
    )
    db_session.add_all([concept1, concept2])
    await db_session.flush()

    prereq = ConceptPrerequisite(
        concept_id=concept2.id,
        prerequisite_id=concept1.id,
        is_hard=True,
    )
    db_session.add(prereq)
    await db_session.commit()

    return domain, subject, concept1, concept2


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")


# Ensure aiosqlite is available
try:
    import aiosqlite
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "aiosqlite"])
    import aiosqlite

