"""user youtube_screenshot

Revision ID: 49a5450ae9c2
Revises: 2e9b25c46ae6
Create Date: 2024-06-07 00:49:15.664639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49a5450ae9c2'
down_revision: Union[str, None] = '2e9b25c46ae6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('youtube_screenshot', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'youtube_screenshot')
    # ### end Alembic commands ###