"""SocialAccount.

Revision ID: 513cd4cbb902
Revises: 746bff5280a9
Create Date: 2022-10-17 08:30:32.755107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "513cd4cbb902"
down_revision = "746bff5280a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "socialaccount",
        sa.Column("advocate_id", sa.UUID(), nullable=False),
        sa.Column("github", sa.String(), nullable=True),
        sa.Column("linkedin", sa.String(), nullable=True),
        sa.Column("youtube", sa.String(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["advocate_id"], ["advocate.id"], name=op.f("fk_socialaccount_advocate_id_advocate")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_socialaccount")),
    )
    op.create_index(op.f("ix_socialaccount_advocate_id"), "socialaccount", ["advocate_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_socialaccount_advocate_id"), table_name="socialaccount")
    op.drop_table("socialaccount")
