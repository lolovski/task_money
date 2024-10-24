"""rs

Revision ID: 6f27f1244377
Revises: 6e2073aa7409
Create Date: 2024-10-12 15:20:56.229147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f27f1244377'
down_revision: Union[str, None] = '6e2073aa7409'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('task', 'count_active',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('task', 'count_active',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
