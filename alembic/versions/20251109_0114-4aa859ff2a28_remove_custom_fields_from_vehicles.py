"""remove_custom_fields_from_vehicles

Revision ID: 4aa859ff2a28
Revises: e288784a42a4
Create Date: 2025-11-09 01:14:58.883689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4aa859ff2a28'
down_revision = 'e288784a42a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove campos customizados que não fazem mais sentido
    # pois agora usamos apenas os relacionamentos com as tabelas brands, models e model_versions
    op.drop_column('vehicles', 'custom_brand')
    op.drop_column('vehicles', 'custom_model')
    op.drop_column('vehicles', 'custom_version')


def downgrade() -> None:
    # Restaura os campos customizados caso seja necessário reverter
    op.add_column('vehicles', sa.Column('custom_version', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('custom_model', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('custom_brand', sa.String(), nullable=True))
