"""merge conflicting migration heads

Revision ID: 3f1873b23ba7
Revises: 0e3f76c187ed, 4f3d43aa6553
Create Date: 2026-07-19 13:13:42.314778

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f1873b23ba7'
down_revision = ('0e3f76c187ed', '4f3d43aa6553')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
