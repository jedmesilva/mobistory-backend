"""add_moment_reactions_table

Revision ID: 0b0f36f5da4a
Revises: a0bb1482016e
Create Date: 2025-10-28 07:28:30.652909

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0b0f36f5da4a'
down_revision = 'a0bb1482016e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # MOMENT_REACTIONS - Reações e comentários em momentos
    # ==========================================================================
    op.create_table(
        'moment_reactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),

        # Relacionamentos
        sa.Column('moment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('moments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_reaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('moment_reactions.id', ondelete='CASCADE')),  # NULL = reação ao post, NOT NULL = reply
        sa.Column('created_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id'), nullable=False),

        # Conteúdo da reação
        sa.Column('reaction_emoji', sa.String()),  # '❤️', '👍', '😂', '😮', '😢', '🔥', etc
        sa.Column('comment', sa.Text()),  # Comentário texto

        # Status
        sa.Column('is_edited', sa.Boolean(), default=False),
        sa.Column('is_deleted', sa.Boolean(), default=False),  # Soft delete para preservar thread

        # Datas
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),

        # Constraint: pelo menos um (emoji ou comment) deve estar preenchido
        sa.CheckConstraint(
            'reaction_emoji IS NOT NULL OR comment IS NOT NULL',
            name='moment_reactions_content_check'
        )
    )

    # Índices para moment_reactions
    op.create_index('idx_moment_reactions_moment_id', 'moment_reactions', ['moment_id'])
    op.create_index('idx_moment_reactions_parent_id', 'moment_reactions', ['parent_reaction_id'])
    op.create_index('idx_moment_reactions_created_by', 'moment_reactions', ['created_by_entity_id'])
    op.create_index('idx_moment_reactions_created_at', 'moment_reactions', ['created_at'])
    op.create_index('idx_moment_reactions_moment_created', 'moment_reactions', ['moment_id', 'created_at'])
    # Índice para threads (listar replies de um comentário)
    op.create_index('idx_moment_reactions_thread', 'moment_reactions', ['parent_reaction_id', 'created_at'])


def downgrade() -> None:
    # Drop índices
    op.drop_index('idx_moment_reactions_thread', table_name='moment_reactions')
    op.drop_index('idx_moment_reactions_moment_created', table_name='moment_reactions')
    op.drop_index('idx_moment_reactions_created_at', table_name='moment_reactions')
    op.drop_index('idx_moment_reactions_created_by', table_name='moment_reactions')
    op.drop_index('idx_moment_reactions_parent_id', table_name='moment_reactions')
    op.drop_index('idx_moment_reactions_moment_id', table_name='moment_reactions')

    # Drop tabela
    op.drop_table('moment_reactions')
