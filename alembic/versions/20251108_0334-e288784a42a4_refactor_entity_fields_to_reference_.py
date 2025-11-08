"""refactor_entity_fields_to_reference_tables

Refatora campos da tabela entities para usar referências:
1. display_name -> primary_name_id (FK para entity_names)
2. email -> primary_email_contact_id (FK para entity_contacts)
3. phone -> primary_phone_contact_id (FK para entity_contacts)
4. profile_picture_url -> profile_picture_id (FK para files)

Revision ID: e288784a42a4
Revises: b2c3d4e5f6g7
Create Date: 2025-11-08 03:34:44.339298

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e288784a42a4'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Adicionar novas colunas de referência à tabela entities
    op.add_column('entities', sa.Column('primary_name_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('entities', sa.Column('primary_email_contact_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('entities', sa.Column('primary_phone_contact_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('entities', sa.Column('profile_picture_id', postgresql.UUID(as_uuid=True), nullable=True))

    # 2. Migrar dados de display_name para entity_names
    op.execute("""
        INSERT INTO entity_names (entity_id, name_type, name_value, is_current, start_date)
        SELECT
            id,
            'display_name' as name_type,
            display_name as name_value,
            true as is_current,
            CURRENT_DATE as start_date
        FROM entities
        WHERE display_name IS NOT NULL AND display_name != ''
    """)

    # 3. Atualizar entities.primary_name_id com os IDs criados
    op.execute("""
        UPDATE entities e
        SET primary_name_id = en.id
        FROM entity_names en
        WHERE e.id = en.entity_id
        AND en.name_type = 'display_name'
        AND en.is_current = true
    """)

    # 4. Migrar dados de email para entity_contacts
    op.execute("""
        INSERT INTO entity_contacts (entity_id, contact_type, contact_value, is_primary, use_for_login, is_active, start_date)
        SELECT
            id,
            'email' as contact_type,
            email as contact_value,
            true as is_primary,
            true as use_for_login,
            true as is_active,
            CURRENT_DATE as start_date
        FROM entities
        WHERE email IS NOT NULL AND email != ''
    """)

    # 5. Atualizar entities.primary_email_contact_id com os IDs criados
    op.execute("""
        UPDATE entities e
        SET primary_email_contact_id = ec.id
        FROM entity_contacts ec
        WHERE e.id = ec.entity_id
        AND ec.contact_type = 'email'
        AND ec.is_primary = true
    """)

    # 6. Migrar dados de phone para entity_contacts
    op.execute("""
        INSERT INTO entity_contacts (entity_id, contact_type, contact_value, is_primary, use_for_login, is_active, start_date)
        SELECT
            id,
            'phone' as contact_type,
            phone as contact_value,
            true as is_primary,
            true as use_for_login,
            true as is_active,
            CURRENT_DATE as start_date
        FROM entities
        WHERE phone IS NOT NULL AND phone != ''
    """)

    # 7. Atualizar entities.primary_phone_contact_id com os IDs criados
    op.execute("""
        UPDATE entities e
        SET primary_phone_contact_id = ec.id
        FROM entity_contacts ec
        WHERE e.id = ec.entity_id
        AND ec.contact_type = 'phone'
        AND ec.is_primary = true
    """)

    # 8. Adicionar foreign keys
    op.create_foreign_key('fk_entities_primary_name', 'entities', 'entity_names', ['primary_name_id'], ['id'])
    op.create_foreign_key('fk_entities_primary_email_contact', 'entities', 'entity_contacts', ['primary_email_contact_id'], ['id'])
    op.create_foreign_key('fk_entities_primary_phone_contact', 'entities', 'entity_contacts', ['primary_phone_contact_id'], ['id'])
    op.create_foreign_key('fk_entities_profile_picture', 'entities', 'files', ['profile_picture_id'], ['id'])

    # 9. Criar índices para melhor performance
    op.create_index('idx_entities_primary_name_id', 'entities', ['primary_name_id'])
    op.create_index('idx_entities_primary_email_contact_id', 'entities', ['primary_email_contact_id'])
    op.create_index('idx_entities_primary_phone_contact_id', 'entities', ['primary_phone_contact_id'])
    op.create_index('idx_entities_profile_picture_id', 'entities', ['profile_picture_id'])

    # 10. Remover as colunas antigas
    op.drop_column('entities', 'display_name')
    op.drop_column('entities', 'email')
    op.drop_column('entities', 'phone')
    op.drop_column('entities', 'profile_picture_url')


def downgrade() -> None:
    # 1. Recriar as colunas antigas
    op.add_column('entities', sa.Column('display_name', sa.String(), nullable=True))
    op.add_column('entities', sa.Column('email', sa.String(), nullable=True))
    op.add_column('entities', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('entities', sa.Column('profile_picture_url', sa.Text(), nullable=True))

    # 2. Restaurar dados de entity_names para display_name
    op.execute("""
        UPDATE entities e
        SET display_name = en.name_value
        FROM entity_names en
        WHERE e.primary_name_id = en.id
    """)

    # 3. Restaurar dados de entity_contacts (email) para email
    op.execute("""
        UPDATE entities e
        SET email = ec.contact_value
        FROM entity_contacts ec
        WHERE e.primary_email_contact_id = ec.id
    """)

    # 4. Restaurar dados de entity_contacts (phone) para phone
    op.execute("""
        UPDATE entities e
        SET phone = ec.contact_value
        FROM entity_contacts ec
        WHERE e.primary_phone_contact_id = ec.id
    """)

    # 5. Remover índices
    op.drop_index('idx_entities_profile_picture_id', 'entities')
    op.drop_index('idx_entities_primary_phone_contact_id', 'entities')
    op.drop_index('idx_entities_primary_email_contact_id', 'entities')
    op.drop_index('idx_entities_primary_name_id', 'entities')

    # 6. Remover foreign keys
    op.drop_constraint('fk_entities_profile_picture', 'entities', type_='foreignkey')
    op.drop_constraint('fk_entities_primary_phone_contact', 'entities', type_='foreignkey')
    op.drop_constraint('fk_entities_primary_email_contact', 'entities', type_='foreignkey')
    op.drop_constraint('fk_entities_primary_name', 'entities', type_='foreignkey')

    # 7. Remover as colunas de referência
    op.drop_column('entities', 'profile_picture_id')
    op.drop_column('entities', 'primary_phone_contact_id')
    op.drop_column('entities', 'primary_email_contact_id')
    op.drop_column('entities', 'primary_name_id')
