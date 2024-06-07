"""user_twitter_username

Revision ID: 9648d786ec2f
Revises: 6d1af7563b50
Create Date: 2024-05-20 03:45:18.018446

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9648d786ec2f'
down_revision: Union[str, None] = '6d1af7563b50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('twitter_username', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'users', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'twitter_username')
    # ### end Alembic commands ###
