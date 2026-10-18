import os

import pytest

# Dont use this as your actual password pepper!
os.environ["PASSWORD_PEPPER"] = "test-pepper"

from app.security import hash_password, hash_token, verify_password


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


def test_hash_token_is_deterministic():
    token = "some-random-token"
    assert hash_token(token) == hash_token(token)


def test_hash_token_differs_for_different_tokens():
    assert hash_token("token-one") != hash_token("token-two")


def test_hash_token_does_not_return_the_original():
    token = "some-random-token"
    assert hash_token(token) != token


def test_hash_token_is_64_characters():
    # SHA-256 as hex is always 64 chars, which fits in the String(255) column
    assert len(hash_token("some-random-token")) == 64
