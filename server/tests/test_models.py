from app.models import User


def test_user_model_has_expected_columns():
    assert hasattr(User, "id")
    assert hasattr(User, "username")
    assert hasattr(User, "password_hash")
    assert hasattr(User, "created_at")
    assert hasattr(User, "is_admin")
