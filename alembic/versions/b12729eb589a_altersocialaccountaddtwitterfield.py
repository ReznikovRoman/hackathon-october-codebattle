"""AlterSocialAccountAddTwitterField.

Revision ID: b12729eb589a
Revises: f736aa6931b1
Create Date: 2022-10-23 14:36:49.624372

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b12729eb589a"
down_revision = "f736aa6931b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("socialaccount", sa.Column("twitter", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("socialaccount", "twitter")
