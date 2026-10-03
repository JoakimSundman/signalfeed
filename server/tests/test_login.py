import pytest
from app.database import session_creator
from app.main import app
from app.models import Session as SessionModel
from app.models import User
from app.security import hash_password
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

client = TestClient(app)

TEST_USERNAME = "pytest_login_user"
TEST_PASSWORD = "pytest-password-123"


@pytest.fixture(scope="module", autouse=True)
def test_user():
    """Creates a known user before tests run, deletes it afterwards.
    Also cleans up before creating, in case a previous run crashed
    mid-teardown and left a stale row behind."""
    session = session_creator()

    def _cleanup():
        stmt = select(User).where(User.username == TEST_USERNAME)
        existing = session.execute(stmt).scalar_one_or_none()
        if existing:
            session.execute(delete(SessionModel).where(SessionModel.user_id == existing.id))
            session.delete(existing)
            session.commit()

    _cleanup()

    user = User(
        username=TEST_USERNAME,
        password_hash=hash_password(TEST_PASSWORD),
        is_admin=False,
    )
    session.add(user)
    session.commit()

    yield

    _cleanup()
    session.close()


def test_login_with_correct_credentials():
    response = client.post("/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_with_wrong_password():
    response = client.post("/login", json={"username": TEST_USERNAME, "password": "Wrong!_123"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Username or password is not correct"}


def test_login_with_nonexistent_username():
    response = client.post("/login", json={"username": "Non_user", "password": TEST_PASSWORD})
    assert response.status_code == 401
    assert response.json() == {"detail": "Username or password is not correct"}
