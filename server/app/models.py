import datetime as dt

import sqlalchemy as db
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

"""
Database models for signalfeed.

Schema overview:
- users: Account holders. is_admin controls who can manage other accounts.
- feeds: Shared, deduplicated RSS/Atom sources — one row per feed regardless
  of how many users subscribe to it.
- articles: Shared article entries per feed, storing only a short summary
  (not full content) plus a link out to the source.
- subscriptions: Per-user link to a feed, with an optional folder/tag for
  organizing the user's feed view.
- article_state: Per-user read/starred status for an article — kept separate
  from `articles` since read status is personal, not shared.

Notes on specific fields:
- guid: the article's unique ID from the feed itself, used to detect
  duplicates when re-fetching (not the same as our own `id`).
- favicon_url / last_fetched_at: nullable, since not all feeds provide a
  favicon and a freshly added feed hasn't been fetched yet.
- published_at: set explicitly by the fetcher from the feed's own data,
  not auto-generated — unlike created_at/added_at which default to "now".
"""


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(db.String(255))
    created_at: Mapped[dt.datetime] = mapped_column(db.DateTime, server_default=func.now())
    is_admin: Mapped[bool] = mapped_column(db.Boolean, default=False)


class Feed(Base):
    __tablename__ = "feeds"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    url: Mapped[str] = mapped_column(db.String(2048), unique=True)
    favicon_url: Mapped[str | None] = mapped_column(db.String(2048))
    title: Mapped[str] = mapped_column(db.String(500))
    last_fetched_at: Mapped[dt.datetime | None] = mapped_column(
        db.DateTime, server_default=func.now()
    )


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    feed_id: Mapped[int] = mapped_column(ForeignKey("feeds.id"))
    guid: Mapped[str] = mapped_column(db.String(2048), unique=True)
    url: Mapped[str] = mapped_column(db.String(2048), unique=True)
    image_url: Mapped[str | None] = mapped_column(db.String(2048))
    title: Mapped[str] = mapped_column(db.String(500))
    summary: Mapped[str] = mapped_column(db.String(500))
    published_at: Mapped[dt.datetime] = mapped_column(db.DateTime)


class ArticleState(Base):
    __tablename__ = "article_state"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    is_read: Mapped[bool] = mapped_column(db.Boolean, default=False)
    is_starred: Mapped[bool] = mapped_column(db.Boolean, default=False)
    updated_at: Mapped[dt.datetime] = mapped_column(db.DateTime)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    feed_id: Mapped[int] = mapped_column(ForeignKey("feeds.id"))
    folder_or_tag: Mapped[str | None] = mapped_column(db.String(100))
    added_at: Mapped[dt.datetime] = mapped_column(db.DateTime)
