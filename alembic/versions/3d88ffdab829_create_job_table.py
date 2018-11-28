"""Create job table

Revision ID: 3d88ffdab829
Revises: 
Create Date: 2018-11-27 13:06:07.639848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d88ffdab829'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jobs',
    sa.Column('job_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('runfolder', sa.String(), nullable=False),
    sa.Column('pid', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('NONE', 'PENDING', 'READY', 'STARTED', 'DONE', 'ERROR', 'CANCELLED', name='status'), nullable=True),
    sa.Column('time_created', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('time_updated', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('job_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('jobs')
    # ### end Alembic commands ###