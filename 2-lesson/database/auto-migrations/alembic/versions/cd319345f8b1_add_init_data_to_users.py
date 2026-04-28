"""add init data to users

Revision ID: cd319345f8b1
Revises: 29b454cb0ab0
Create Date: 2025-09-19 12:00:32.648934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd319345f8b1'
down_revision: Union[str, Sequence[str], None] = '29b454cb0ab0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    users_table = sa.table('users', sa.column('name', sa.String), sa.column('email', sa.String))

    op.bulk_insert(users_table, [{"name": "John", "email": "john@example.com"}, {"name": "Jane", "email": "jane@example.com"}])


def downgrade() -> None:
    users_table = sa.table('users', sa.column('email', sa.String))
    op.execute(users_table.delete().where(users_table.c.email.in_(["john@example.com", "jane@example.com"])))

