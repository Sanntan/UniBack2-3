"""add_article_url_column

Revision ID: d9674af8ec72
Revises: 10f8a1f9e42a
Create Date: 2025-04-10 20:28:26.802655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9674af8ec72'
down_revision: Union[str, None] = '10f8a1f9e42a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('article', sa.Column('article_url', sa.String(length=512)))

def downgrade():
    op.drop_column('article', 'article_url')
