"""PhotoField.

Revision ID: 03a6396eecc3
Revises: f75e1218ca7d
Create Date: 2022-10-17 14:23:56.767779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "03a6396eecc3"
down_revision = "f75e1218ca7d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("advocate", sa.Column("photo_url", sa.String(), nullable=True))
    op.add_column("company", sa.Column("photo_url", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("company", "photo_url")
    op.drop_column("advocate", "photo_url")
