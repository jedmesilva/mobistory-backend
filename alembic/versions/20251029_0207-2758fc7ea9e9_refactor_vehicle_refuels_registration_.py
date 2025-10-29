"""refactor_vehicle_refuels_registration_logic

Refatora a lógica de registro em vehicle_refuels:
- Adiciona registered_by_entity_id (obrigatório) - quem/o que registrou
- Remove registered_by_link_id (redundante)
- link_id permanece opcional - contexto do vínculo quando aplicável

Cenários:
1. Motorista abastece: registered_by_entity_id=João, link_id=link do João
2. Bomba IoT: registered_by_entity_id=Posto Shell, link_id=NULL
3. Sistema/API: registered_by_entity_id=Sistema, link_id=link do motorista (se souber)
4. Terceiro: registered_by_entity_id=Maria, link_id=NULL

Revision ID: 2758fc7ea9e9
Revises: 0b0f36f5da4a
Create Date: 2025-10-29 02:07:09.978812

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2758fc7ea9e9'
down_revision = '0b0f36f5da4a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Adicionar coluna registered_by_entity_id (inicialmente nullable)
    op.add_column('vehicle_refuels',
        sa.Column('registered_by_entity_id', postgresql.UUID(as_uuid=True), nullable=True)
    )

    # 2. Preencher registered_by_entity_id com dados de registered_by_link_id quando possível
    # Para registros existentes, vamos copiar a entidade do link
    op.execute("""
        UPDATE vehicle_refuels vr
        SET registered_by_entity_id = l.entity_id
        FROM links l
        WHERE vr.registered_by_link_id = l.id
    """)

    # 3. Para registros sem link, usar a entidade do link principal do veículo
    op.execute("""
        UPDATE vehicle_refuels vr
        SET registered_by_entity_id = l.entity_id
        FROM links l
        WHERE vr.registered_by_entity_id IS NULL
        AND vr.link_id = l.id
    """)

    # 4. Tornar registered_by_entity_id NOT NULL
    op.alter_column('vehicle_refuels', 'registered_by_entity_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False
    )

    # 5. Adicionar foreign key constraint
    op.create_foreign_key(
        'vehicle_refuels_registered_by_entity_id_fkey',
        'vehicle_refuels', 'entities',
        ['registered_by_entity_id'], ['id']
    )

    # 6. Remover foreign key de registered_by_link_id
    op.drop_constraint('vehicle_refuels_registered_by_link_id_fkey', 'vehicle_refuels', type_='foreignkey')

    # 7. Remover coluna registered_by_link_id
    op.drop_column('vehicle_refuels', 'registered_by_link_id')


def downgrade() -> None:
    # 1. Adicionar coluna registered_by_link_id de volta
    op.add_column('vehicle_refuels',
        sa.Column('registered_by_link_id', postgresql.UUID(as_uuid=True), nullable=True)
    )

    # 2. Tentar restaurar dados (usar link_id quando disponível)
    op.execute("""
        UPDATE vehicle_refuels
        SET registered_by_link_id = link_id
        WHERE link_id IS NOT NULL
    """)

    # 3. Adicionar foreign key de volta
    op.create_foreign_key(
        'vehicle_refuels_registered_by_link_id_fkey',
        'vehicle_refuels', 'links',
        ['registered_by_link_id'], ['id']
    )

    # 4. Remover foreign key de registered_by_entity_id
    op.drop_constraint('vehicle_refuels_registered_by_entity_id_fkey', 'vehicle_refuels', type_='foreignkey')

    # 5. Remover coluna registered_by_entity_id
    op.drop_column('vehicle_refuels', 'registered_by_entity_id')
