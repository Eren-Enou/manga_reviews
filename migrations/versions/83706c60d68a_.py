"""empty message

Revision ID: 83706c60d68a
Revises: cbc2d633caa9
Create Date: 2023-04-24 10:37:52.987063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83706c60d68a'
down_revision = 'cbc2d633caa9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('manga',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('genres', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=1000), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('manga')
    # ### end Alembic commands ###
