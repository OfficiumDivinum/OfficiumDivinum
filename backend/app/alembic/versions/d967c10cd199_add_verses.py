"""add verses

Revision ID: d967c10cd199
Revises: 0309f585cb29
Create Date: 2021-02-25 15:24:10.221221

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd967c10cd199'
down_revision = '0309f585cb29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('verse',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('rubrics', sa.String(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('verse', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verse_id'), 'verse', ['id'], unique=False)
    op.create_index(op.f('ix_verse_rubrics'), 'verse', ['rubrics'], unique=False)
    op.create_index(op.f('ix_verse_title'), 'verse', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_verse_title'), table_name='verse')
    op.drop_index(op.f('ix_verse_rubrics'), table_name='verse')
    op.drop_index(op.f('ix_verse_id'), table_name='verse')
    op.drop_table('verse')
    # ### end Alembic commands ###
