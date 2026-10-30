"""store resume file paths relative to FILES_DIR

Uploads used to store paths relative to the backend's working directory
("../files/resumes/8.pdf"). They are now relative to FILES_DIR
("resumes/8.pdf").

Revision ID: ed0f70a867de
Revises: df775c301f09
Create Date: 2026-10-29 19:22:18.235470

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ed0f70a867de'
down_revision: Union[str, Sequence[str], None] = 'df775c301f09'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        UPDATE resumes
        SET file_path = substr(file_path, length('../files/') + 1)
        WHERE file_path LIKE '../files/%'
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        UPDATE resumes
        SET file_path = '../files/' || file_path
        WHERE file_path IS NOT NULL
          AND file_path NOT LIKE '/%'
          AND file_path NOT LIKE '../files/%'
        """
    )
