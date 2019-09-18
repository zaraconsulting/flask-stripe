"""empty message

Revision ID: ad60218e5c41
Revises: 553fcb9041bd
Create Date: 2019-09-18 12:05:20.286564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad60218e5c41'
down_revision = '553fcb9041bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('id_', sa.String(), nullable=False))
    op.drop_column('product', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.drop_column('product', 'id_')
    # ### end Alembic commands ###
