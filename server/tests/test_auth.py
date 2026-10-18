from datetime import datetime, timedelta, timezone

import pytest
from app.database import session_creator
from app.main import app
from app.models import Session as SessionModel
from app.models import User
from app.security import hash_password, hash_token
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


def test_login_stores_hashed_token_not_plaintext():
    response = client.post("/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    token = response.json()["token"]

    session = session_creator()
    try:
        hashed_stmt = select(SessionModel).where(SessionModel.token_hash == hash_token(token))
        plaintext_stmt = select(SessionModel).where(SessionModel.token_hash == token)

        hashed_row = session.execute(hashed_stmt).scalar_one_or_none()
        plaintext_row = session.execute(plaintext_stmt).scalar_one_or_none()
    finally:
        session.close()

    assert hashed_row is not None
    assert plaintext_row is None


def login_and_get_token():
    response = client.post("/login", json={"username": TEST_USERNAME, "password": TEST_PASSWORD})
    return response.json()["token"]


def test_me_without_header_returns_401():
    response = client.get("/me")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_me_with_wrong_scheme_returns_401():
    response = client.get("/me", headers={"Authorization": "Basic abc123"})
    assert response.status_code == 401


def test_me_with_unknown_token_returns_401():
    response = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_me_with_expired_token_returns_401():
    token = "expired-test-token"

    session = session_creator()
    try:
        user = session.execute(select(User).where(User.username == TEST_USERNAME)).scalar_one()
        session.add(
            SessionModel(
                user_id=user.id,
                token_hash=hash_token(token),
                expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            )
        )
        session.commit()
    finally:
        session.close()

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_me_with_valid_token_returns_user_without_password_hash():
    token = login_and_get_token()
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == TEST_USERNAME
    assert "password_hash" not in response.json()


def test_logout_invalidates_token():
    token = login_and_get_token()
    headers = {"Authorization": f"Bearer {token}"}

    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 204

    me_response = client.get("/me", headers=headers)
    assert me_response.status_code == 401

    second_logout = client.post("/logout", headers=headers)
    assert second_logout.status_code == 401
