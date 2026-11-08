from datetime import datetime, timezone

import pytest
from app.database import session_creator
from app.models import Article, ArticleState, Feed, Subscription, User
from app.models import Session as SessionModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def db():
    session = session_creator()
    yield session
    session.rollback()  # nothing is ever committed
    session.close()


def make_user(db, name):
    user = User(username=name, password_hash="x", is_admin=False)
    db.add(user)
    db.flush()
    return user


def make_feed(db, url):
    feed = Feed(url=url, title="test feed")
    db.add(feed)
    db.flush()
    return feed


def make_article(db, feed, guid):
    article = Article(
        feed_id=feed.id,
        guid=guid,
        url=f"https://example.com/{guid}",
        title="t",
        summary="s",
        published_at=datetime.now(timezone.utc),
    )
    db.add(article)
    db.flush()
    return article


def test_duplicate_subscription_is_rejected(db):
    user = make_user(db, "constraint_user")
    feed = make_feed(db, "https://example.com/feed-a")
    db.add(Subscription(user_id=user.id, feed_id=feed.id))
    db.flush()
    db.add(Subscription(user_id=user.id, feed_id=feed.id))
    with pytest.raises(IntegrityError):
        db.flush()


def test_duplicate_article_state_is_rejected(db):
    user = make_user(db, "constraint_user")
    feed = make_feed(db, "https://example.com/feed-a")
    article = make_article(db, feed, "guid-1")
    db.add(ArticleState(user_id=user.id, article_id=article.id))
    db.flush()
    db.add(ArticleState(user_id=user.id, article_id=article.id))
    with pytest.raises(IntegrityError):
        db.flush()


def test_same_guid_allowed_in_different_feeds_but_not_in_same_feed(db):
    feed_a = make_feed(db, "https://example.com/feed-a")
    feed_b = make_feed(db, "https://example.com/feed-b")
    make_article(db, feed_a, "shared-guid")
    make_article(db, feed_b, "shared-guid")  # different feed: allowed

    with pytest.raises(IntegrityError):
        make_article(db, feed_a, "shared-guid")  # same feed: rejected


def test_deleting_user_cascades_to_sessions(db):
    user = make_user(db, "constraint_user")
    db.add(
        SessionModel(
            user_id=user.id,
            token_hash="cascade-test-hash",
            expires_at=datetime.now(timezone.utc),
        )
    )
    db.flush()

    db.delete(user)
    db.flush()

    stmt = select(SessionModel).where(SessionModel.token_hash == "cascade-test-hash")
    assert db.execute(stmt).scalar_one_or_none() is None


def test_deleting_feed_with_subscription_is_restricted(db):
    user = make_user(db, "constraint_user")
    feed = make_feed(db, "https://example.com/feed-a")
    db.add(Subscription(user_id=user.id, feed_id=feed.id))
    db.flush()

    db.delete(feed)
    with pytest.raises(IntegrityError):
        db.flush()
