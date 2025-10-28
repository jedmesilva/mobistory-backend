"""implement_complete_mobistory_structure

Revision ID: 0b985f927bf7
Revises:
Create Date: 2025-10-28 05:05:18.083279

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0b985f927bf7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # CORE ENTITIES & TYPES
    # ==========================================================================

    # Entity Types
    op.create_table(
        'entity_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('code', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('requires_cpf', sa.Boolean(), default=False),
        sa.Column('requires_cnpj', sa.Boolean(), default=False),
        sa.Column('requires_special_id', sa.Boolean(), default=False),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Entities
    op.create_table(
        'entities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_code', sa.String(), nullable=False, unique=True),
        sa.Column('entity_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entity_types.id')),
        sa.Column('legal_id_number', sa.String(), unique=True),
        sa.Column('global_key_hash', sa.String()),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('email', sa.String()),
        sa.Column('phone', sa.String()),
        sa.Column('profile_picture_url', sa.Text()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ==========================================================================
    # VEHICLE CATALOG
    # ==========================================================================

    # Brands
    op.create_table(
        'brands',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('country_of_origin', sa.String()),
        sa.Column('logo_url', sa.Text()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Models
    op.create_table(
        'models',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('brands.id')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Model Versions
    op.create_table(
        'model_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('models.id')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('start_year', sa.Integer()),
        sa.Column('end_year', sa.Integer()),
        sa.Column('fuel_type', sa.String()),
        sa.Column('transmission', sa.String()),
        sa.Column('drive_type', sa.String()),
        sa.Column('engine_displacement', sa.Numeric()),
        sa.Column('engine_power', sa.Integer()),
        sa.Column('doors', sa.Integer()),
        sa.Column('seats', sa.Integer()),
        sa.Column('weight_kg', sa.Integer()),
        sa.Column('tank_capacity_liters', sa.Integer()),
        sa.Column('trunk_capacity_liters', sa.Integer()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Vehicles
    op.create_table(
        'vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vin', sa.String(), unique=True),
        sa.Column('renavam', sa.String(), unique=True),
        sa.Column('brand_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('brands.id')),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('models.id')),
        sa.Column('version_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('model_versions.id')),
        sa.Column('custom_brand', sa.String()),
        sa.Column('custom_model', sa.String()),
        sa.Column('custom_version', sa.String()),
        sa.Column('manufacturing_year', sa.Integer()),
        sa.Column('model_year', sa.Integer()),
        sa.Column('current_color', sa.String()),
        sa.Column('current_plate', sa.String()),
        sa.Column('current_km', sa.Integer()),
        sa.Column('visibility', sa.String(), default='private'),
        sa.Column('observations', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ==========================================================================
    # LINKS & PERMISSIONS
    # ==========================================================================

    # Link Types
    op.create_table(
        'link_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('code', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('permissions', postgresql.JSONB()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Links
    op.create_table(
        'links',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('link_code', sa.String(), nullable=False, unique=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id')),
        sa.Column('link_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('link_types.id')),
        sa.Column('own_key_hash', sa.String()),
        sa.Column('uses_own_key', sa.Boolean(), default=False),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('document_proof', sa.Text()),
        sa.Column('validated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('validated_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('start_date', sa.Date()),
        sa.Column('end_date', sa.Date()),
        sa.Column('observations', sa.Text()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Link Status History
    op.create_table(
        'link_status',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('from_status', sa.String()),
        sa.Column('to_status', sa.String(), nullable=False),
        sa.Column('changed_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('changed_by_link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('reason', sa.Text()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # ==========================================================================
    # VEHICLE CLAIMS
    # ==========================================================================

    # Vehicle Claims
    op.create_table(
        'vehicle_claims',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id')),
        sa.Column('link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('claim_type', sa.String()),
        sa.Column('severity', sa.String()),
        sa.Column('claim_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('claim_km', sa.Integer()),
        sa.Column('location_lat', sa.Numeric()),
        sa.Column('location_lng', sa.Numeric()),
        sa.Column('address', sa.Text()),
        sa.Column('police_report', sa.String()),
        sa.Column('police_report_url', sa.Text()),
        sa.Column('insurance_company', sa.String()),
        sa.Column('claim_number', sa.String()),
        sa.Column('policy', sa.String()),
        sa.Column('insurance_status', sa.String()),
        sa.Column('indemnity_value', sa.Numeric()),
        sa.Column('tow_truck_called', sa.Boolean()),
        sa.Column('tow_truck_company', sa.String()),
        sa.Column('involved_third_parties', postgresql.JSONB()),
        sa.Column('description', sa.Text()),
        sa.Column('photos_urls', sa.Text()),
        sa.Column('total_repair_cost', sa.Numeric()),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ==========================================================================
    # FUEL INFRASTRUCTURE
    # ==========================================================================

    # Fuel Types
    op.create_table(
        'fuel_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('code', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('unit', sa.String()),
        sa.Column('hex_color', sa.String()),
        sa.Column('icon', sa.String()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Flags
    op.create_table(
        'flags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('code', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('logo_url', sa.Text()),
        sa.Column('country_of_origin', sa.String()),
        sa.Column('website', sa.String()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Fuel Stations
    op.create_table(
        'fuel_stations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('cnpj', sa.String()),
        sa.Column('location_lat', sa.Numeric()),
        sa.Column('location_lng', sa.Numeric()),
        sa.Column('address', sa.Text()),
        sa.Column('city', sa.String()),
        sa.Column('state', sa.String()),
        sa.Column('postal_code', sa.String()),
        sa.Column('country', sa.String()),
        sa.Column('phone', sa.String()),
        sa.Column('email', sa.String()),
        sa.Column('website', sa.String()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Fuel Station Flags
    op.create_table(
        'fuel_station_flags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('station_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fuel_stations.id')),
        sa.Column('flag_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('flags.id')),
        sa.Column('start_date', sa.Date()),
        sa.Column('end_date', sa.Date()),
        sa.Column('observations', sa.Text()),
        sa.Column('registered_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Station Fuels
    op.create_table(
        'station_fuels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('station_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fuel_stations.id')),
        sa.Column('fuel_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fuel_types.id')),
        sa.Column('start_date', sa.Date()),
        sa.Column('end_date', sa.Date()),
        sa.Column('status', sa.String(), default='active'),
        sa.Column('observations', sa.Text()),
        sa.Column('registered_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Station Fuel Prices
    op.create_table(
        'station_fuel_prices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('station_fuel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('station_fuels.id')),
        sa.Column('price', sa.Numeric(), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date()),
        sa.Column('is_promotion', sa.Boolean(), default=False),
        sa.Column('promotion_description', sa.Text()),
        sa.Column('reported_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('verified', sa.Boolean(), default=False),
        sa.Column('verified_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('verified_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Fuel Station Hours
    op.create_table(
        'fuel_station_hours',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('station_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fuel_stations.id')),
        sa.Column('day_of_week', sa.Integer()),
        sa.Column('opens_at', sa.Time()),
        sa.Column('closes_at', sa.Time()),
        sa.Column('is_24_hours', sa.Boolean(), default=False),
        sa.Column('is_closed', sa.Boolean(), default=False),
        sa.Column('start_date', sa.Date()),
        sa.Column('end_date', sa.Date()),
        sa.Column('observations', sa.Text()),
        sa.Column('registered_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Fuel Station Operating Periods
    op.create_table(
        'fuel_station_operating_periods',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('station_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fuel_stations.id')),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('first_activity_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('last_activity_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('total_refuels', sa.Integer()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ==========================================================================
    # VEHICLE OPERATIONS
    # ==========================================================================

    # Vehicle Refuels
    op.create_table(
        'vehicle_refuels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id')),
        sa.Column('link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('station_fuel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('station_fuels.id')),
        sa.Column('fuel_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fuel_types.id')),
        sa.Column('station_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fuel_stations.id')),
        sa.Column('refuel_date', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('refuel_km', sa.Integer()),
        sa.Column('quantity', sa.Numeric(), nullable=False),
        sa.Column('unit_price', sa.Numeric()),
        sa.Column('total_price', sa.Numeric()),
        sa.Column('full_tank', sa.Boolean(), default=False),
        sa.Column('invoice_url', sa.Text()),
        sa.Column('observations', sa.Text()),
        sa.Column('registered_by_link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Odometers
    op.create_table(
        'odometers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id')),
        sa.Column('installation_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('removal_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('brand', sa.String()),
        sa.Column('model', sa.String()),
        sa.Column('part_number', sa.String()),
        sa.Column('cost', sa.Numeric()),
        sa.Column('supplier', sa.String()),
        sa.Column('invoice_url', sa.Text()),
        sa.Column('warranty_months', sa.Integer()),
        sa.Column('warranty_km', sa.Integer()),
        sa.Column('reason_for_change', sa.Text()),
        sa.Column('damage_type', sa.String()),
        sa.Column('observations', sa.Text()),
        sa.Column('registered_by_link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Mileage Records
    op.create_table(
        'mileage_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('odometer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('odometers.id')),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id')),
        sa.Column('recorded_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('mileage', sa.Integer(), nullable=False),
        sa.Column('registered_by_link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # ==========================================================================
    # CONVERSATIONS & AI
    # ==========================================================================

    # Conversation Contexts
    op.create_table(
        'conversation_contexts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('code', sa.String(), nullable=False, unique=True),
        sa.Column('category', sa.String()),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('keywords', postgresql.JSONB()),
        sa.Column('available_actions', postgresql.JSONB()),
        sa.Column('ai_instructions', sa.Text()),
        sa.Column('requires_link', sa.Boolean(), default=False),
        sa.Column('required_permissions', postgresql.JSONB()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Conversations
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_code', sa.String(), nullable=False, unique=True),
        sa.Column('primary_vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id')),
        sa.Column('vehicle_ids', sa.Text()),
        sa.Column('conversation_type', sa.String()),
        sa.Column('title', sa.String()),
        sa.Column('summary', sa.Text()),
        sa.Column('status', sa.String(), default='active'),
        sa.Column('main_context_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversation_contexts.id')),
        sa.Column('total_participants', sa.Integer(), default=0),
        sa.Column('active_participants', sa.Integer(), default=0),
        sa.Column('total_messages', sa.Integer(), default=0),
        sa.Column('total_actions_executed', sa.Integer(), default=0),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('last_message_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('finished_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('archived_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Conversation Participants
    op.create_table(
        'conversation_participants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('role', sa.String()),
        sa.Column('participant_type', sa.String()),
        sa.Column('joined_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('left_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('invited_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('invited_by_participant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversation_participants.id')),
        sa.Column('invitation_reason', sa.String()),
        sa.Column('removed_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('removal_reason', sa.String()),
        sa.Column('permissions', postgresql.JSONB()),
        sa.Column('context_summary_at_join', sa.Text()),
        sa.Column('auto_leave_config', postgresql.JSONB()),
        sa.Column('notification_enabled', sa.Boolean(), default=True),
        sa.Column('last_read_message_id', postgresql.UUID(as_uuid=True)),
        sa.Column('last_read_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('unread_count', sa.Integer(), default=0),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # ==========================================================================
    # ACTIONS
    # ==========================================================================

    # Action Types
    op.create_table(
        'action_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('code', sa.String(), nullable=False, unique=True),
        sa.Column('category', sa.String()),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('icon', sa.String()),
        sa.Column('color', sa.String()),
        sa.Column('requires_execution', sa.Boolean(), default=False),
        sa.Column('affects_database', sa.Boolean(), default=True),
        sa.Column('affects_physical_vehicle', sa.Boolean(), default=False),
        sa.Column('input_schema', postgresql.JSONB()),
        sa.Column('output_schema', postgresql.JSONB()),
        sa.Column('required_permissions', postgresql.JSONB()),
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Actions
    op.create_table(
        'actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id')),
        sa.Column('action_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('action_types.id')),
        sa.Column('created_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('created_by_link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('assigned_to_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('executed_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('executed_by_link_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('links.id')),
        sa.Column('source_type', sa.String()),
        sa.Column('source_id', postgresql.UUID(as_uuid=True)),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id')),
        sa.Column('parent_action_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('actions.id')),
        sa.Column('title', sa.String()),
        sa.Column('description', sa.Text()),
        sa.Column('input_data', postgresql.JSONB()),
        sa.Column('output_data', postgresql.JSONB()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('status', sa.String(), default='pendente'),
        sa.Column('priority', sa.Integer()),
        sa.Column('scheduled_for', sa.TIMESTAMP(timezone=True)),
        sa.Column('schedule_type', sa.String()),
        sa.Column('recurrence_rule', sa.Text()),
        sa.Column('execution_order', sa.Integer()),
        sa.Column('depends_on_action_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('actions.id')),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True)),
        sa.Column('is_atomic', sa.Boolean(), default=False),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('executed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('cancelled_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('error_message', sa.Text()),
        sa.Column('retry_count', sa.Integer(), default=0),
        sa.Column('max_retries', sa.Integer()),
        sa.Column('affected_entities', postgresql.JSONB()),
        sa.Column('rollback_data', postgresql.JSONB()),
        sa.Column('requires_confirmation', sa.Boolean(), default=False),
        sa.Column('confirmed_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('confirmed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('location_lat', sa.Numeric()),
        sa.Column('location_lng', sa.Numeric()),
        sa.Column('address', sa.Text()),
        sa.Column('estimated_cost', sa.Numeric()),
        sa.Column('actual_cost', sa.Numeric()),
        sa.Column('currency', sa.String()),
        sa.Column('attachments_urls', sa.Text()),
        sa.Column('external_references', postgresql.JSONB()),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('alert_before_hours', sa.Integer()),
        sa.Column('alerted_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Action Status History
    op.create_table(
        'action_status',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('action_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('actions.id')),
        sa.Column('from_status', sa.String()),
        sa.Column('to_status', sa.String(), nullable=False),
        sa.Column('changed_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('reason', sa.Text()),
        sa.Column('metadata', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Action Notes
    op.create_table(
        'action_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('action_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('actions.id')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('note_type', sa.String()),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('attachments_urls', sa.Text()),
        sa.Column('is_internal', sa.Boolean(), default=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Conversation Messages
    op.create_table(
        'conversation_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id')),
        sa.Column('sender_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('sender_participant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversation_participants.id')),
        sa.Column('directed_to_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('directed_to_participant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversation_participants.id')),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String()),
        sa.Column('context_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversation_contexts.id')),
        sa.Column('context_confidence', sa.Numeric()),
        sa.Column('detected_intent', sa.String()),
        sa.Column('extracted_entities', postgresql.JSONB()),
        sa.Column('action_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('actions.id')),
        sa.Column('action_executed', sa.Boolean(), default=False),
        sa.Column('action_result', postgresql.JSONB()),
        sa.Column('requires_confirmation', sa.Boolean(), default=False),
        sa.Column('confirmed', sa.Boolean(), default=False),
        sa.Column('confirmed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('confirmed_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('attachments_urls', sa.Text()),
        sa.Column('visible_to_participant_ids', sa.Text()),
        sa.Column('is_private', sa.Boolean(), default=False),
        sa.Column('requires_user_interaction', sa.Boolean(), default=False),
        sa.Column('interaction_reason', sa.String()),
        sa.Column('auto_processed', sa.Boolean(), default=False),
        sa.Column('processed', sa.Boolean(), default=False),
        sa.Column('processed_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('reactions', postgresql.JSONB()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # ==========================================================================
    # INDEXES
    # ==========================================================================

    # Indexes para melhor performance
    op.create_index('idx_entities_entity_code', 'entities', ['entity_code'])
    op.create_index('idx_entities_legal_id_number', 'entities', ['legal_id_number'])
    op.create_index('idx_vehicles_vin', 'vehicles', ['vin'])
    op.create_index('idx_vehicles_renavam', 'vehicles', ['renavam'])
    op.create_index('idx_vehicles_current_plate', 'vehicles', ['current_plate'])
    op.create_index('idx_links_link_code', 'links', ['link_code'])
    op.create_index('idx_links_status', 'links', ['status'])
    op.create_index('idx_links_entity_vehicle', 'links', ['entity_id', 'vehicle_id'])
    op.create_index('idx_conversations_code', 'conversations', ['conversation_code'])
    op.create_index('idx_conversations_status', 'conversations', ['status'])
    op.create_index('idx_conversation_messages_conversation', 'conversation_messages', ['conversation_id'])
    op.create_index('idx_actions_vehicle', 'actions', ['vehicle_id'])
    op.create_index('idx_actions_status', 'actions', ['status'])
    op.create_index('idx_actions_conversation', 'actions', ['conversation_id'])
    op.create_index('idx_vehicle_refuels_vehicle', 'vehicle_refuels', ['vehicle_id'])
    op.create_index('idx_vehicle_refuels_date', 'vehicle_refuels', ['refuel_date'])
    op.create_index('idx_mileage_records_vehicle', 'mileage_records', ['vehicle_id'])
    op.create_index('idx_mileage_records_date', 'mileage_records', ['recorded_at'])


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('conversation_messages')
    op.drop_table('action_notes')
    op.drop_table('action_status')
    op.drop_table('actions')
    op.drop_table('action_types')
    op.drop_table('conversation_participants')
    op.drop_table('conversations')
    op.drop_table('conversation_contexts')
    op.drop_table('mileage_records')
    op.drop_table('odometers')
    op.drop_table('vehicle_refuels')
    op.drop_table('fuel_station_operating_periods')
    op.drop_table('fuel_station_hours')
    op.drop_table('station_fuel_prices')
    op.drop_table('station_fuels')
    op.drop_table('fuel_station_flags')
    op.drop_table('fuel_stations')
    op.drop_table('flags')
    op.drop_table('fuel_types')
    op.drop_table('vehicle_claims')
    op.drop_table('link_status')
    op.drop_table('links')
    op.drop_table('link_types')
    op.drop_table('vehicles')
    op.drop_table('model_versions')
    op.drop_table('models')
    op.drop_table('brands')
    op.drop_table('entities')
    op.drop_table('entity_types')
