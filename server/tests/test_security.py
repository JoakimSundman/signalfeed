import os

import pytest

# Dont use this as your actual password pepper!
os.environ["PASSWORD_PEPPER"] = "test-pepper"

from app.security import hash_password, verify_password


def test_hash_password_and_verify_correct_password():
    password = "test"
    password_hash = hash_password(password)
    assert verify_password(password, password_hash)


def test_verify_password_rejects_wrong_password():
    password = "test"
    wrong_password = "security"
    password_hash = hash_password(password)
    assert not verify_password(wrong_password, password_hash)


def test_hash_password_reject_non_string():
    with pytest.raises(TypeError):
        hash_password(12345)
