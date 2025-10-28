"""add_description_to_colors_table

Revision ID: 451a37a90810
Revises: c70c9b6970ee
Create Date: 2025-10-28 05:30:53.018088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '451a37a90810'
down_revision = 'c70c9b6970ee'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar campo description na tabela colors
    # Para descrições detalhadas como "Azul Marinho Perolizado", "Vermelho Metálico", etc
    op.add_column('colors', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remover campo description da tabela colors
    op.drop_column('colors', 'description')
