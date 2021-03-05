"""prayer

Revision ID: 4437530c007d
Revises: af308525fd3c
Create Date: 2021-03-03 19:30:26.429721

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4437530c007d'
down_revision = 'af308525fd3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('prayer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('rubrics', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('crossref', sa.String(), nullable=True),
    sa.Column('version', sa.String(), nullable=True),
    sa.Column('type_', sa.String(), nullable=True),
    sa.Column('at', sa.PickleType(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prayer_crossref'), 'prayer', ['crossref'], unique=False)
    op.create_index(op.f('ix_prayer_id'), 'prayer', ['id'], unique=False)
    op.create_index(op.f('ix_prayer_language'), 'prayer', ['language'], unique=False)
    op.create_index(op.f('ix_prayer_rubrics'), 'prayer', ['rubrics'], unique=False)
    op.create_index(op.f('ix_prayer_title'), 'prayer', ['title'], unique=False)
    op.create_index(op.f('ix_prayer_type_'), 'prayer', ['type_'], unique=False)
    op.create_index(op.f('ix_prayer_version'), 'prayer', ['version'], unique=False)
    op.create_table('prayerline',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rubrics', sa.String(), nullable=True),
    sa.Column('prefix', sa.String(), nullable=True),
    sa.Column('suffix', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('lineno', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prayerline_content'), 'prayerline', ['content'], unique=False)
    op.create_index(op.f('ix_prayerline_id'), 'prayerline', ['id'], unique=False)
    op.create_index(op.f('ix_prayerline_prefix'), 'prayerline', ['prefix'], unique=False)
    op.create_index(op.f('ix_prayerline_rubrics'), 'prayerline', ['rubrics'], unique=False)
    op.create_index(op.f('ix_prayerline_suffix'), 'prayerline', ['suffix'], unique=False)
    op.create_table('prayer_line_association_table',
    sa.Column('prayerline_id', sa.Integer(), nullable=False),
    sa.Column('prayer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['prayer_id'], ['prayer.id'], ),
    sa.ForeignKeyConstraint(['prayerline_id'], ['prayerline.id'], ),
    sa.PrimaryKeyConstraint('prayerline_id', 'prayer_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('prayer_line_association_table')
    op.drop_index(op.f('ix_prayerline_suffix'), table_name='prayerline')
    op.drop_index(op.f('ix_prayerline_rubrics'), table_name='prayerline')
    op.drop_index(op.f('ix_prayerline_prefix'), table_name='prayerline')
    op.drop_index(op.f('ix_prayerline_id'), table_name='prayerline')
    op.drop_index(op.f('ix_prayerline_content'), table_name='prayerline')
    op.drop_table('prayerline')
    op.drop_index(op.f('ix_prayer_version'), table_name='prayer')
    op.drop_index(op.f('ix_prayer_type_'), table_name='prayer')
    op.drop_index(op.f('ix_prayer_title'), table_name='prayer')
    op.drop_index(op.f('ix_prayer_rubrics'), table_name='prayer')
    op.drop_index(op.f('ix_prayer_language'), table_name='prayer')
    op.drop_index(op.f('ix_prayer_id'), table_name='prayer')
    op.drop_index(op.f('ix_prayer_crossref'), table_name='prayer')
    op.drop_table('prayer')
    # ### end Alembic commands ###