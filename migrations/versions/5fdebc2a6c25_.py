"""empty message

Revision ID: 5fdebc2a6c25
Revises: 8fe3dfadac40
Create Date: 2024-10-06 22:27:44.353921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fdebc2a6c25'
down_revision = '8fe3dfadac40'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shelter', schema=None) as batch_op:
        batch_op.add_column(sa.Column('other', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shelter', schema=None) as batch_op:
        batch_op.drop_column('other')

    # ### end Alembic commands ###
