"""add_verified_field_to_brands_models_versions

Revision ID: c2f8af2d9399
Revises: cd903dcd4b4e
Create Date: 2025-11-03 01:43:15.065110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2f8af2d9399'
down_revision = 'cd903dcd4b4e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar campo verified em brands
    op.add_column('brands', sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'))

    # Adicionar campo verified em models
    op.add_column('models', sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'))

    # Adicionar campo verified em model_versions
    op.add_column('model_versions', sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remover campo verified de model_versions
    op.drop_column('model_versions', 'verified')

    # Remover campo verified de models
    op.drop_column('models', 'verified')

    # Remover campo verified de brands
    op.drop_column('brands', 'verified')
