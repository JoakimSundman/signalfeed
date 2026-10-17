"""rename sessions.token to token_hash

Revision ID: 70dc7e24422d
Revises: c85b51b50334
Create Date: 2026-10-17 10:24:32.474218

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "70dc7e24422d"
down_revision: Union[str, Sequence[str], None] = "c85b51b50334"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("sessions", "token", new_column_name="token_hash")
    op.execute(
        "ALTER TABLE sessions RENAME CONSTRAINT sessions_token_key TO sessions_token_hash_key"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "ALTER TABLE sessions RENAME CONSTRAINT sessions_token_hash_key TO sessions_token_key"
    )
    op.alter_column("sessions", "token_hash", new_column_name="token")
