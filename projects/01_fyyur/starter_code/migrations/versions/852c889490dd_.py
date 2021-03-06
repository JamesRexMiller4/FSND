"""empty message

Revision ID: 852c889490dd
Revises: c8f81b8a4ffd
Create Date: 2020-04-08 12:03:20.724963

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '852c889490dd'
down_revision = 'c8f81b8a4ffd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'website',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('venue', 'website',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###
