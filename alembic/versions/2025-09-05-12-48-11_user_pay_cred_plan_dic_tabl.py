"""user_pay_cred_plan_dic_tabl

Revision ID: 78990858e670
Revises:
Create Date: 2025-09-05 12:48:11.442566

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "78990858e670"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "dictionary",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("login", sa.String(length=64), nullable=False),
        sa.Column("registration_date", sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("login"),
    )
    op.create_table(
        "credits",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("issuance_date", sa.Date(), nullable=False),
        sa.Column("return_date", sa.Date(), nullable=True),
        sa.Column("actual_return_date", sa.Date(), nullable=True),
        sa.Column("body", sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column("percent", sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_credits_user_id"), "credits", ["user_id"], unique=False)
    op.create_table(
        "plans",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("period", sa.Date(), nullable=False),
        sa.Column("sum", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["dictionary.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("sum", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("credit_id", sa.BigInteger(), nullable=False),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["credit_id"],
            ["credits.id"],
        ),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["dictionary.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("payments")
    op.drop_table("plans")
    op.drop_index(op.f("ix_credits_user_id"), table_name="credits")
    op.drop_table("credits")
    op.drop_table("users")
    op.drop_table("dictionary")
