"""Advocate initial.

Revision ID: 746bff5280a9
Revises:
Create Date: 2022-10-16 16:26:36.443335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "746bff5280a9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "advocate",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("short_bio", sa.String(), nullable=False),
        sa.Column("long_bio", sa.String(), nullable=False),
        sa.Column("years_of_experience", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("years_of_experience >= 0", name=op.f("ck_advocate_years_of_experience_non_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_advocate")),
    )


def downgrade() -> None:
    op.drop_table("advocate")
