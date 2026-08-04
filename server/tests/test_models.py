from app.models import Article, Feed, User


def test_user_model_has_expected_columns():
    assert hasattr(User, "id")
    assert hasattr(User, "username")
    assert hasattr(User, "password_hash")
    assert hasattr(User, "created_at")
    assert hasattr(User, "is_admin")


def test_feed_model_has_expected_columns():
    assert hasattr(Feed, "id")
    assert hasattr(Feed, "url")
    assert hasattr(Feed, "favicon_url")
    assert hasattr(Feed, "title")
    assert hasattr(Feed, "last_fetched_at")


def test_article_model_has_expected_columns():
    assert hasattr(Article, "id")
    assert hasattr(Article, "feed_id")
    assert hasattr(Article, "guid")
    assert hasattr(Article, "url")
    assert hasattr(Article, "image_url")
    assert hasattr(Article, "title")
    assert hasattr(Article, "summary")
    assert hasattr(Article, "published_at")
