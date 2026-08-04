import datetime as dt

import sqlalchemy as db
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


"""
User model:
- id: Unique identifier for the user (primary key)
- username: Unique username for the user (string, max length 50)
- password_hash: Hashed password for the user (string, max length 255)
- created_at: Date and time of creation (datetime)
- is_admin: Bool to identify if user is an admin (bool)
"""


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(db.String(255))
    created_at: Mapped[dt.datetime] = mapped_column(db.DateTime, server_default=func.now())
    is_admin: Mapped[bool] = mapped_column(db.Boolean, default=False)


"""
Feed model: 
- id: Unique identifier for the feed (primary key)
- url: The url / link to the feed (String, max length 2048, unique)
- favicon_url: Url for the favicon (String, max length 2048)
- title: Title of feed (string, max length 500)
- last_fetched_at: Date and time of last fetched (datetime)
"""


class Feed(Base):
    __tablename__ = "feeds"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    url: Mapped[str] = mapped_column(db.String(2048), unique=True)
    favicon_url: Mapped[str | None] = mapped_column(db.String(2048))
    title: Mapped[str] = mapped_column(db.String(500))
    last_fetched_at: Mapped[dt.datetime | None] = mapped_column(
        db.DateTime, server_default=func.now()
    )


"""
Article model:
- id: Unique identifier for the article (primary key)
- feed_id: Foreign key to feed for the article 
- guid: Unique identifier for the article from the feed itself, 
        used to detect duplicates when re-fetching 
        (String, max length 2048, unique)
- url: The url / link to the article (String, max length 2048)
- image_url: Url to the image (String or None, max length 2048)
- title: Title of article (String, max length 500)
- summary: Summary of article (String, max length 500)
- published_at: Date and time of publication (datetime)
"""


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
