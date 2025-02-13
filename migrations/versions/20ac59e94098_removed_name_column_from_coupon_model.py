"""removed name column from coupon model

Revision ID: 20ac59e94098
Revises: 996ca686aa0d
Create Date: 2019-09-18 16:55:36.816341

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20ac59e94098'
down_revision = '996ca686aa0d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coupon', 'percent_off',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=True)
    op.drop_column('coupon', 'name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coupon', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('coupon', 'percent_off',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               nullable=False)
    # ### end Alembic commands ###
