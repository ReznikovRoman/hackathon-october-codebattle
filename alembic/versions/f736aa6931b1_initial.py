"""Initial.

Revision ID: f736aa6931b1
Revises:
Create Date: 2022-10-17 14:35:30.831056

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f736aa6931b1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "company",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("summary", sa.String(), nullable=False),
        sa.Column("photo_url", sa.String(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_company")),
    )
    op.create_index(op.f("ix_company_name"), "company", ["name"], unique=True)

    op.create_table(
        "advocate",
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("short_bio", sa.String(), nullable=False),
        sa.Column("long_bio", sa.String(), nullable=False),
        sa.Column("years_of_experience", sa.Integer(), nullable=False),
        sa.Column("photo_url", sa.String(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("years_of_experience >= 0", name=op.f("ck_advocate_years_of_experience_non_negative")),
        sa.ForeignKeyConstraint(["company_id"], ["company.id"], name=op.f("fk_advocate_company_id_company")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_advocate")),
    )
    op.create_index(op.f("ix_advocate_company_id"), "advocate", ["company_id"], unique=False)

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
    op.create_index(op.f("ix_socialaccount_advocate_id"), "socialaccount", ["advocate_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_socialaccount_advocate_id"), table_name="socialaccount")
    op.drop_table("socialaccount")

    op.drop_index(op.f("ix_advocate_company_id"), table_name="advocate")
    op.drop_table("advocate")

    op.drop_index(op.f("ix_company_name"), table_name="company")
    op.drop_table("company")
