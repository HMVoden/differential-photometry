"""variable

Revision ID: 1d18993b0dcc
Revises: 00fb40a87f48
Create Date: 2022-03-03 17:56:41.216812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d18993b0dcc'
down_revision = '00fb40a87f48'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stars', sa.Column('variable', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stars', 'variable')
    # ### end Alembic commands ###
