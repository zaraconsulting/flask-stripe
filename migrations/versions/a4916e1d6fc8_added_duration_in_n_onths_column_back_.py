"""added duration_in_n_onths column back to coupon model

Revision ID: a4916e1d6fc8
Revises: 01782d1b54bb
Create Date: 2019-09-18 17:00:23.928807

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4916e1d6fc8'
down_revision = '01782d1b54bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coupon', sa.Column('duration_in_months', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('coupon', 'duration_in_months')
    # ### end Alembic commands ###
