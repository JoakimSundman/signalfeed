"""add constraints, on delete rules and, defaults

Revision ID: 1145d8593770
Revises: 70dc7e24422d
Create Date: 2026-10-23 10:27:21.339417

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1145d8593770"
down_revision: Union[str, Sequence[str], None] = "70dc7e24422d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # unique constraints
    op.create_unique_constraint(
        "uq_article_state_user_id_article_id", "article_state", ["user_id", "article_id"]
    )
    op.drop_constraint("articles_guid_key", "articles", type_="unique")
    op.drop_constraint("articles_url_key", "articles", type_="unique")
    op.create_unique_constraint("uq_articles_feed_id_guid", "articles", ["feed_id", "guid"])
    op.create_unique_constraint(
        "uq_subscriptions_user_id_feed_id", "subscriptions", ["user_id", "feed_id"]
    )

    # foreign keys: recreate with ON DELETE rules (explicit names)
    for table in ("article_state", "sessions", "subscriptions"):
        op.drop_constraint(f"{table}_user_id_fkey", table, type_="foreignkey")
        op.create_foreign_key(
            f"{table}_user_id_fkey", table, "users", ["user_id"], ["id"], ondelete="CASCADE"
        )
    op.drop_constraint("article_state_article_id_fkey", "article_state", type_="foreignkey")
    op.create_foreign_key(
        "article_state_article_id_fkey",
        "article_state",
        "articles",
        ["article_id"],
        ["id"],
        ondelete="CASCADE",
    )
    for table in ("articles", "subscriptions"):
        op.drop_constraint(f"{table}_feed_id_fkey", table, type_="foreignkey")
        op.create_foreign_key(
            f"{table}_feed_id_fkey", table, "feeds", ["feed_id"], ["id"], ondelete="RESTRICT"
        )

    # server defaults (not detected by autogenerate)
    op.alter_column(
        "subscriptions",
        "added_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "article_state",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "feeds",
        "last_fetched_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "feeds",
        "last_fetched_at",
        existing_type=sa.DateTime(timezone=True),
        existing_nullable=True,
        server_default=sa.text("now()"),
    )
    op.alter_column(
        "article_state",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
    )
    op.alter_column(
        "subscriptions",
        "added_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
    )

    for table in ("article_state", "sessions", "subscriptions"):
        op.drop_constraint(f"{table}_user_id_fkey", table, type_="foreignkey")
        op.create_foreign_key(f"{table}_user_id_fkey", table, "users", ["user_id"], ["id"])
    op.drop_constraint("article_state_article_id_fkey", "article_state", type_="foreignkey")
    op.create_foreign_key(
        "article_state_article_id_fkey", "article_state", "articles", ["article_id"], ["id"]
    )
    for table in ("articles", "subscriptions"):
        op.drop_constraint(f"{table}_feed_id_fkey", table, type_="foreignkey")
        op.create_foreign_key(f"{table}_feed_id_fkey", table, "feeds", ["feed_id"], ["id"])

    op.drop_constraint("uq_subscriptions_user_id_feed_id", "subscriptions", type_="unique")
    op.drop_constraint("uq_articles_feed_id_guid", "articles", type_="unique")
    op.create_unique_constraint("articles_url_key", "articles", ["url"])
    op.create_unique_constraint("articles_guid_key", "articles", ["guid"])
    op.drop_constraint("uq_article_state_user_id_article_id", "article_state", type_="unique")
