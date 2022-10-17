"""SocialAccountAdvocateUnique.

Revision ID: e072cf2da2e1
Revises: 513cd4cbb902
Create Date: 2022-10-17 08:53:52.815245

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "e072cf2da2e1"
down_revision = "513cd4cbb902"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_socialaccount_advocate_id", table_name="socialaccount")
    op.create_index(op.f("ix_socialaccount_advocate_id"), "socialaccount", ["advocate_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_socialaccount_advocate_id"), table_name="socialaccount")
    op.create_index("ix_socialaccount_advocate_id", "socialaccount", ["advocate_id"], unique=False)
