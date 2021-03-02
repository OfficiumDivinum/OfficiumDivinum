"""perhaps not there yet?

Revision ID: 74b1aa3c6e1d
Revises: 0b05efd6ab5d
Create Date: 2021-03-01 19:52:49.491853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74b1aa3c6e1d'
down_revision = '0b05efd6ab5d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_hymn_verse_id', table_name='hymnverse')
    op.drop_index('ix_hymn_verse_rubrics', table_name='hymnverse')
    op.drop_index('ix_hymn_verse_title', table_name='hymnverse')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_hymn_verse_title', 'hymnverse', ['title'], unique=False)
    op.create_index('ix_hymn_verse_rubrics', 'hymnverse', ['rubrics'], unique=False)
    op.create_index('ix_hymn_verse_id', 'hymnverse', ['id'], unique=False)
    # ### end Alembic commands ###