import datetime as dt

import sqlalchemy as db
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


"""
User model containing:
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
