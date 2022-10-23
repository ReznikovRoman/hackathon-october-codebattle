"""AlterAdvocateAddUsername.

Revision ID: ba261f0697dd
Revises: b12729eb589a
Create Date: 2022-10-23 14:42:48.475637

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ba261f0697dd"
down_revision = "b12729eb589a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("advocate", sa.Column("username", sa.String(), nullable=True))

    op.execute("UPDATE advocate SET username=concat(replace(name, ' ', ''), '_', id)")
    op.alter_column("advocate", "username", nullable=False)

    op.create_index(op.f("ix_advocate_username"), "advocate", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_advocate_username"), table_name="advocate")
    op.drop_column("advocate", "username")
