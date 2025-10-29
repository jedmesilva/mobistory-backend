"""add_entity_extended_tables

Adiciona tabelas estendidas para o sistema de entidades:
1. entity_relationships - Hierarquia e relacionamentos entre entidades
2. entity_names - Histórico de nomes (legal, display, nickname, etc)
3. entity_identifications - Documentos de identificação (CPF, CNPJ, RG, CNH, etc)
4. entity_contacts - Contatos (email, telefone, whatsapp, api_endpoint, etc)
5. entity_credentials - Credenciais de autenticação (password, pin, api_key, mfa)
6. entity_credential_attempts - Histórico de tentativas de autenticação

Revision ID: cd903dcd4b4e
Revises: 2758fc7ea9e9
Create Date: 2025-10-29 03:14:08.874717

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cd903dcd4b4e'
down_revision = '2758fc7ea9e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # 1. ENTITY_RELATIONSHIPS - Hierarquia e relacionamentos entre entidades
    # ==========================================================================
    op.create_table(
        'entity_relationships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=False),  # owns, subsidiary, branch, equipment, division, partner
        sa.Column('start_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('end_date', sa.Date()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('reason', sa.Text()),
        sa.Column('observations', sa.Text()),
        sa.Column('created_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),

        # Constraint: Não pode ser pai de si mesmo
        sa.CheckConstraint('entity_id != parent_entity_id', name='entity_relationships_no_self_parent')
    )

    # Índices para entity_relationships
    op.create_index('idx_entity_relationships_entity', 'entity_relationships', ['entity_id'])
    op.create_index('idx_entity_relationships_parent', 'entity_relationships', ['parent_entity_id'])
    op.create_index('idx_entity_relationships_entity_active', 'entity_relationships', ['entity_id', 'is_active'])
    op.create_index('idx_entity_relationships_parent_active', 'entity_relationships', ['parent_entity_id', 'is_active'])
    op.create_index('idx_entity_relationships_pair', 'entity_relationships', ['entity_id', 'parent_entity_id', 'is_active'])
    op.create_index('idx_entity_relationships_type', 'entity_relationships', ['relationship_type'])

    # ==========================================================================
    # 2. ENTITY_NAMES - Histórico de nomes
    # ==========================================================================
    op.create_table(
        'entity_names',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name_type', sa.String(), nullable=False),  # legal_name, display_name, nickname, alias, trade_name
        sa.Column('name_value', sa.String(), nullable=False),
        sa.Column('is_current', sa.Boolean(), default=True),
        sa.Column('start_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('end_date', sa.Date()),
        sa.Column('reason', sa.String()),  # marriage, divorce, legal_change, correction, preference
        sa.Column('changed_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('observations', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para entity_names
    op.create_index('idx_entity_names_entity', 'entity_names', ['entity_id'])
    op.create_index('idx_entity_names_entity_current', 'entity_names', ['entity_id', 'is_current'])
    op.create_index('idx_entity_names_type_current', 'entity_names', ['entity_id', 'name_type', 'is_current'])
    op.create_index('idx_entity_names_value', 'entity_names', ['name_value'])

    # ==========================================================================
    # 3. ENTITY_IDENTIFICATIONS - Documentos de identificação
    # ==========================================================================
    op.create_table(
        'entity_identifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('identification_type', sa.String(), nullable=False),  # CPF, CNPJ, RG, CNH, Passport, Serial_Number
        sa.Column('identification_number', sa.String(), nullable=False),
        sa.Column('issuing_country', sa.String()),
        sa.Column('issuing_state', sa.String()),
        sa.Column('issuing_authority', sa.String()),
        sa.Column('issue_date', sa.Date()),
        sa.Column('expiry_date', sa.Date()),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verified_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('verified_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('start_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('end_date', sa.Date()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para entity_identifications
    op.create_index('idx_entity_identifications_entity', 'entity_identifications', ['entity_id'])
    op.create_index('idx_entity_identifications_primary', 'entity_identifications', ['entity_id', 'is_primary', 'is_active'])
    op.create_index('idx_entity_identifications_type_number', 'entity_identifications', ['identification_type', 'identification_number'])
    op.create_index('idx_entity_identifications_number', 'entity_identifications', ['identification_number'])

    # ==========================================================================
    # 4. ENTITY_CONTACTS - Contatos
    # ==========================================================================
    op.create_table(
        'entity_contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('contact_type', sa.String(), nullable=False),  # email, phone, whatsapp, api_endpoint, mqtt_topic
        sa.Column('contact_value', sa.String(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verified_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('is_public', sa.Boolean(), default=False),
        sa.Column('use_for_login', sa.Boolean(), default=False),
        sa.Column('use_for_recovery', sa.Boolean(), default=False),
        sa.Column('use_for_notifications', sa.Boolean(), default=True),
        sa.Column('use_for_2fa', sa.Boolean(), default=False),
        sa.Column('label', sa.String()),  # "Pessoal", "Trabalho", "Recuperação"
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('start_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('end_date', sa.Date()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para entity_contacts
    op.create_index('idx_entity_contacts_entity', 'entity_contacts', ['entity_id'])
    op.create_index('idx_entity_contacts_entity_type', 'entity_contacts', ['entity_id', 'contact_type'])
    op.create_index('idx_entity_contacts_primary', 'entity_contacts', ['entity_id', 'is_primary'])
    op.create_index('idx_entity_contacts_recovery', 'entity_contacts', ['entity_id', 'use_for_recovery', 'is_verified'])
    op.create_index('idx_entity_contacts_login', 'entity_contacts', ['entity_id', 'use_for_login', 'is_verified'])
    op.create_index('idx_entity_contacts_value', 'entity_contacts', ['contact_value'])

    # ==========================================================================
    # 5. ENTITY_CREDENTIALS - Credenciais de autenticação
    # ==========================================================================
    op.create_table(
        'entity_credentials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('credential_type', sa.String(), nullable=False),  # password, pin, api_key, mfa_secret
        sa.Column('credential_hash', sa.Text(), nullable=False),
        sa.Column('hash_algorithm', sa.String(), nullable=False),  # argon2id, bcrypt
        sa.Column('salt', sa.String()),
        sa.Column('iterations', sa.Integer()),
        sa.Column('is_current', sa.Boolean(), default=True),
        sa.Column('is_compromised', sa.Boolean(), default=False),
        sa.Column('compromised_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('compromised_reason', sa.Text()),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('last_used_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('failed_attempts', sa.Integer(), default=0),
        sa.Column('locked_until', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('creation_method', sa.String()),  # self_service, admin_reset, system_generated
        sa.Column('creation_ip', sa.String()),
        sa.Column('replaced_credential_id', postgresql.UUID(as_uuid=True)),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # FK para replaced_credential_id (self-reference)
    op.create_foreign_key(
        'entity_credentials_replaced_credential_id_fkey',
        'entity_credentials', 'entity_credentials',
        ['replaced_credential_id'], ['id'],
        ondelete='SET NULL'
    )

    # Índices para entity_credentials
    op.create_index('idx_entity_credentials_entity', 'entity_credentials', ['entity_id'])
    op.create_index('idx_entity_credentials_current', 'entity_credentials', ['entity_id', 'is_current', 'credential_type'])
    op.create_index('idx_entity_credentials_type', 'entity_credentials', ['entity_id', 'credential_type'])
    op.create_index('idx_entity_credentials_expires', 'entity_credentials', ['expires_at'])

    # ==========================================================================
    # 6. ENTITY_CREDENTIAL_ATTEMPTS - Tentativas de autenticação
    # ==========================================================================
    op.create_table(
        'entity_credential_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('credential_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entity_credentials.id', ondelete='SET NULL')),
        sa.Column('attempt_type', sa.String(), nullable=False),  # login, password_change, password_reset
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String()),  # wrong_password, account_locked, expired
        sa.Column('ip_address', sa.String()),
        sa.Column('user_agent', sa.Text()),
        sa.Column('device_fingerprint', sa.String()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Índices para entity_credential_attempts
    op.create_index('idx_credential_attempts_entity', 'entity_credential_attempts', ['entity_id'])
    op.create_index('idx_credential_attempts_entity_date', 'entity_credential_attempts', ['entity_id', 'created_at'])
    op.create_index('idx_credential_attempts_credential', 'entity_credential_attempts', ['credential_id'])
    op.create_index('idx_credential_attempts_success', 'entity_credential_attempts', ['success'])
    op.create_index('idx_credential_attempts_date', 'entity_credential_attempts', ['created_at'])


def downgrade() -> None:
    # Remover tabelas na ordem inversa
    op.drop_table('entity_credential_attempts')
    op.drop_table('entity_credentials')
    op.drop_table('entity_contacts')
    op.drop_table('entity_identifications')
    op.drop_table('entity_names')
    op.drop_table('entity_relationships')
