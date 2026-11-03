"""one analysis per resume

Keeps only the latest analysis (highest id) for each resume, which is the
one the app already used, and adds a unique constraint on resume_id.
Downgrading removes the constraint but cannot restore the deleted rows.

Revision ID: 8b38113ffed2
Revises: ed0f70a867de
Create Date: 2026-11-03 05:07:20.761877

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '8b38113ffed2'
down_revision: Union[str, Sequence[str], None] = 'ed0f70a867de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        DELETE FROM resume_analyses AS older
        USING resume_analyses AS newer
        WHERE older.resume_id = newer.resume_id
          AND older.id < newer.id
        """
    )
    # Name matches Postgres' default for UNIQUE (resume_id)
    op.create_unique_constraint(
        'resume_analyses_resume_id_key',
        'resume_analyses',
        ['resume_id'],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'resume_analyses_resume_id_key',
        'resume_analyses',
        type_='unique',
    )
