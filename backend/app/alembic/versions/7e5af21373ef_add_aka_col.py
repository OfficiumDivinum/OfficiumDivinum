"""add aka col

Revision ID: 7e5af21373ef
Revises: d03fa1b4be98
Create Date: 2021-02-25 19:46:19.656020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e5af21373ef'
down_revision = 'd03fa1b4be98'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('verse', sa.Column('aka', sa.String(), nullable=True))
    op.create_index(op.f('ix_verse_aka'), 'verse', ['aka'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_verse_aka'), table_name='verse')
    op.drop_column('verse', 'aka')
    # ### end Alembic commands ###