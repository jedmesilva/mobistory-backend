--
-- PostgreSQL database dump
--

\restrict z2F9fdzZ7yj5AMiiADaeubNCCDzPMPbvSbnEZy6UEReW97U0gdwldaAEHTugkjb

-- Dumped from database version 16.10
-- Dumped by pg_dump version 16.10

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: action_notes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.action_notes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    action_id uuid,
    entity_id uuid,
    note_type character varying,
    content text NOT NULL,
    attachments_urls text,
    is_internal boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: action_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.action_status (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    action_id uuid,
    from_status character varying,
    to_status character varying NOT NULL,
    changed_by_entity_id uuid,
    reason text,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: action_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.action_types (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying NOT NULL,
    category character varying,
    name character varying NOT NULL,
    description text,
    icon character varying,
    color character varying,
    requires_execution boolean,
    affects_database boolean,
    affects_physical_vehicle boolean,
    input_schema jsonb,
    output_schema jsonb,
    required_permissions jsonb,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: actions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.actions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vehicle_id uuid,
    action_type_id uuid,
    created_by_entity_id uuid,
    created_by_link_id uuid,
    assigned_to_entity_id uuid,
    executed_by_entity_id uuid,
    executed_by_link_id uuid,
    source_type character varying,
    source_id uuid,
    conversation_id uuid,
    parent_action_id uuid,
    title character varying,
    description text,
    input_data jsonb,
    output_data jsonb,
    metadata jsonb,
    status character varying,
    priority integer,
    scheduled_for timestamp with time zone,
    schedule_type character varying,
    recurrence_rule text,
    execution_order integer,
    depends_on_action_id uuid,
    batch_id uuid,
    is_atomic boolean,
    started_at timestamp with time zone,
    executed_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    error_message text,
    retry_count integer,
    max_retries integer,
    affected_entities jsonb,
    rollback_data jsonb,
    requires_confirmation boolean,
    confirmed_by_entity_id uuid,
    confirmed_at timestamp with time zone,
    location_lat numeric,
    location_lng numeric,
    address text,
    estimated_cost numeric,
    actual_cost numeric,
    currency character varying,
    attachments_urls text,
    external_references jsonb,
    expires_at timestamp with time zone,
    alert_before_hours integer,
    alerted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: brands; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.brands (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    country_of_origin character varying,
    logo_url text,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: colors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.colors (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vehicle_id uuid NOT NULL,
    color character varying NOT NULL,
    hex_code character varying,
    start_date date,
    end_date date,
    created_by_entity_id uuid,
    active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    description text
);


--
-- Name: conversation_contexts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversation_contexts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying NOT NULL,
    category character varying,
    name character varying NOT NULL,
    description text,
    keywords jsonb,
    available_actions jsonb,
    ai_instructions text,
    requires_link boolean,
    required_permissions jsonb,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: conversation_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversation_messages (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    conversation_id uuid,
    sender_entity_id uuid,
    sender_participant_id uuid,
    directed_to_entity_id uuid,
    directed_to_participant_id uuid,
    content text NOT NULL,
    message_type character varying,
    context_id uuid,
    context_confidence numeric,
    detected_intent character varying,
    extracted_entities jsonb,
    action_id uuid,
    action_executed boolean,
    action_result jsonb,
    requires_confirmation boolean,
    confirmed boolean,
    confirmed_at timestamp with time zone,
    confirmed_by_entity_id uuid,
    attachments_urls text,
    visible_to_participant_ids text,
    is_private boolean,
    requires_user_interaction boolean,
    interaction_reason character varying,
    auto_processed boolean,
    processed boolean,
    processed_at timestamp with time zone,
    reactions jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: conversation_participants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversation_participants (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    conversation_id uuid,
    entity_id uuid,
    link_id uuid,
    role character varying,
    participant_type character varying,
    joined_at timestamp with time zone,
    left_at timestamp with time zone,
    is_active boolean,
    invited_by_entity_id uuid,
    invited_by_participant_id uuid,
    invitation_reason character varying,
    removed_by_entity_id uuid,
    removal_reason character varying,
    permissions jsonb,
    context_summary_at_join text,
    auto_leave_config jsonb,
    notification_enabled boolean,
    last_read_message_id uuid,
    last_read_at timestamp with time zone,
    unread_count integer,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: conversations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.conversations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    conversation_code character varying NOT NULL,
    primary_vehicle_id uuid,
    vehicle_ids text,
    conversation_type character varying,
    title character varying,
    summary text,
    status character varying,
    main_context_id uuid,
    total_participants integer,
    active_participants integer,
    total_messages integer,
    total_actions_executed integer,
    started_at timestamp with time zone,
    last_message_at timestamp with time zone,
    finished_at timestamp with time zone,
    archived_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: entities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_code character varying NOT NULL,
    entity_type_id uuid,
    legal_id_number character varying,
    global_key_hash character varying,
    display_name character varying NOT NULL,
    email character varying,
    phone character varying,
    profile_picture_url text,
    metadata jsonb,
    active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: entity_documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_id uuid NOT NULL,
    file_id uuid NOT NULL,
    document_type character varying,
    document_number character varying,
    issue_date date,
    expiry_date date,
    issuing_authority character varying,
    is_verified boolean,
    verified_at timestamp with time zone,
    verified_by_entity_id uuid,
    is_current boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: entity_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_types (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying NOT NULL,
    name character varying NOT NULL,
    description text,
    requires_cpf boolean,
    requires_cnpj boolean,
    requires_special_id boolean,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.files (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vehicle_id uuid,
    uploaded_by_entity_id uuid NOT NULL,
    file_url text NOT NULL,
    file_name character varying,
    file_type character varying,
    mime_type character varying,
    file_size_bytes bigint,
    width integer,
    height integer,
    duration_seconds integer,
    source character varying,
    status character varying,
    uploaded_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: flags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.flags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying NOT NULL,
    name character varying NOT NULL,
    logo_url text,
    country_of_origin character varying,
    website character varying,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: fuel_station_flags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fuel_station_flags (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    flag_id uuid,
    start_date date,
    end_date date,
    observations text,
    registered_by_entity_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: fuel_station_hours; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fuel_station_hours (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    day_of_week integer,
    opens_at time without time zone,
    closes_at time without time zone,
    is_24_hours boolean,
    is_closed boolean,
    start_date date,
    end_date date,
    observations text,
    registered_by_entity_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: fuel_station_operating_periods; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fuel_station_operating_periods (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    date date NOT NULL,
    first_activity_at timestamp with time zone,
    last_activity_at timestamp with time zone,
    total_refuels integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: fuel_stations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fuel_stations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    cnpj character varying,
    location_lat numeric,
    location_lng numeric,
    address text,
    city character varying,
    state character varying,
    postal_code character varying,
    country character varying,
    phone character varying,
    email character varying,
    website character varying,
    active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: fuel_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fuel_types (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying NOT NULL,
    name character varying NOT NULL,
    description text,
    unit character varying,
    hex_color character varying,
    icon character varying,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: link_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.link_status (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    link_id uuid,
    from_status character varying,
    to_status character varying NOT NULL,
    changed_by_entity_id uuid,
    changed_by_link_id uuid,
    reason text,
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: link_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.link_types (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying NOT NULL,
    name character varying NOT NULL,
    description text,
    permissions jsonb,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: links; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.links (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    link_code character varying NOT NULL,
    entity_id uuid,
    vehicle_id uuid,
    link_type_id uuid,
    own_key_hash character varying,
    uses_own_key boolean,
    status character varying,
    document_proof text,
    validated_at timestamp with time zone,
    validated_by uuid,
    start_date date,
    end_date date,
    observations text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: mileage_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mileage_records (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    odometer_id uuid,
    vehicle_id uuid,
    recorded_at timestamp with time zone NOT NULL,
    mileage integer NOT NULL,
    registered_by_link_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: model_versions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.model_versions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    model_id uuid,
    name character varying NOT NULL,
    start_year integer,
    end_year integer,
    fuel_type character varying,
    transmission character varying,
    drive_type character varying,
    engine_displacement numeric,
    engine_power integer,
    doors integer,
    seats integer,
    weight_kg integer,
    tank_capacity_liters integer,
    trunk_capacity_liters integer,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: models; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.models (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    brand_id uuid,
    name character varying NOT NULL,
    category character varying,
    active boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: moment_contents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.moment_contents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    moment_id uuid NOT NULL,
    file_id uuid NOT NULL,
    display_order integer,
    is_cover boolean,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: moment_descriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.moment_descriptions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    moment_id uuid NOT NULL,
    description text NOT NULL,
    edited_by_entity_id uuid NOT NULL,
    is_current boolean,
    edit_reason character varying,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: moment_reactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.moment_reactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    moment_id uuid NOT NULL,
    parent_reaction_id uuid,
    created_by_entity_id uuid NOT NULL,
    reaction_emoji character varying,
    comment text,
    is_edited boolean,
    is_deleted boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    CONSTRAINT moment_reactions_content_check CHECK (((reaction_emoji IS NOT NULL) OR (comment IS NOT NULL)))
);


--
-- Name: moment_vehicles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.moment_vehicles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    moment_id uuid NOT NULL,
    vehicle_id uuid NOT NULL,
    tagged_by_entity_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: moments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.moments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_by_entity_id uuid NOT NULL,
    status character varying,
    visibility character varying,
    location_lat numeric(10,7),
    location_lng numeric(10,7),
    location_name character varying,
    recorded_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: odometers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.odometers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vehicle_id uuid,
    installation_date timestamp with time zone,
    removal_date timestamp with time zone,
    brand character varying,
    model character varying,
    part_number character varying,
    cost numeric,
    supplier character varying,
    invoice_url text,
    warranty_months integer,
    warranty_km integer,
    reason_for_change text,
    damage_type character varying,
    observations text,
    registered_by_link_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: plate_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.plate_types (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code character varying NOT NULL,
    name character varying NOT NULL,
    description text,
    country character varying NOT NULL,
    format_pattern character varying,
    format_example character varying,
    active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: plates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.plates (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vehicle_id uuid NOT NULL,
    plate_type_id uuid NOT NULL,
    plate_number character varying NOT NULL,
    licensing_date date,
    licensing_country character varying,
    state character varying,
    city character varying,
    status character varying,
    end_date date,
    created_by_entity_id uuid,
    active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: station_fuel_prices; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.station_fuel_prices (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_fuel_id uuid,
    price numeric NOT NULL,
    effective_date date NOT NULL,
    end_date date,
    is_promotion boolean,
    promotion_description text,
    reported_by_entity_id uuid,
    verified boolean,
    verified_at timestamp with time zone,
    verified_by_entity_id uuid,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: station_fuels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.station_fuels (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    station_id uuid,
    fuel_type_id uuid,
    start_date date,
    end_date date,
    status character varying,
    observations text,
    registered_by_entity_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: vehicle_claims; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicle_claims (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vehicle_id uuid,
    link_id uuid,
    claim_type character varying,
    severity character varying,
    claim_date timestamp with time zone,
    claim_km integer,
    location_lat numeric,
    location_lng numeric,
    address text,
    police_report character varying,
    police_report_url text,
    insurance_company character varying,
    claim_number character varying,
    policy character varying,
    insurance_status character varying,
    indemnity_value numeric,
    tow_truck_called boolean,
    tow_truck_company character varying,
    involved_third_parties jsonb,
    description text,
    photos_urls text,
    total_repair_cost numeric,
    status character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: vehicle_covers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicle_covers (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vehicle_id uuid NOT NULL,
    file_id uuid NOT NULL,
    is_primary boolean,
    display_order integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: vehicle_refuels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicle_refuels (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vehicle_id uuid,
    link_id uuid,
    station_fuel_id uuid,
    fuel_type_id uuid,
    station_id uuid,
    refuel_date timestamp with time zone NOT NULL,
    refuel_km integer,
    quantity numeric NOT NULL,
    unit_price numeric,
    total_price numeric,
    full_tank boolean,
    invoice_url text,
    observations text,
    registered_by_link_id uuid,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: vehicles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vehicles (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    vin character varying,
    renavam character varying,
    brand_id uuid,
    model_id uuid,
    version_id uuid,
    custom_brand character varying,
    custom_model character varying,
    custom_version character varying,
    manufacturing_year integer,
    model_year integer,
    current_color character varying,
    current_plate character varying,
    current_km integer,
    visibility character varying,
    observations text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: action_notes action_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_notes
    ADD CONSTRAINT action_notes_pkey PRIMARY KEY (id);


--
-- Name: action_status action_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_status
    ADD CONSTRAINT action_status_pkey PRIMARY KEY (id);


--
-- Name: action_types action_types_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_types
    ADD CONSTRAINT action_types_code_key UNIQUE (code);


--
-- Name: action_types action_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_types
    ADD CONSTRAINT action_types_pkey PRIMARY KEY (id);


--
-- Name: actions actions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: brands brands_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.brands
    ADD CONSTRAINT brands_pkey PRIMARY KEY (id);


--
-- Name: colors colors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.colors
    ADD CONSTRAINT colors_pkey PRIMARY KEY (id);


--
-- Name: conversation_contexts conversation_contexts_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_contexts
    ADD CONSTRAINT conversation_contexts_code_key UNIQUE (code);


--
-- Name: conversation_contexts conversation_contexts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_contexts
    ADD CONSTRAINT conversation_contexts_pkey PRIMARY KEY (id);


--
-- Name: conversation_messages conversation_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_messages
    ADD CONSTRAINT conversation_messages_pkey PRIMARY KEY (id);


--
-- Name: conversation_participants conversation_participants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_pkey PRIMARY KEY (id);


--
-- Name: conversations conversations_conversation_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_conversation_code_key UNIQUE (conversation_code);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: entities entities_entity_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT entities_entity_code_key UNIQUE (entity_code);


--
-- Name: entities entities_legal_id_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT entities_legal_id_number_key UNIQUE (legal_id_number);


--
-- Name: entities entities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT entities_pkey PRIMARY KEY (id);


--
-- Name: entity_documents entity_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_documents
    ADD CONSTRAINT entity_documents_pkey PRIMARY KEY (id);


--
-- Name: entity_types entity_types_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_types
    ADD CONSTRAINT entity_types_code_key UNIQUE (code);


--
-- Name: entity_types entity_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_types
    ADD CONSTRAINT entity_types_pkey PRIMARY KEY (id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (id);


--
-- Name: flags flags_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flags
    ADD CONSTRAINT flags_code_key UNIQUE (code);


--
-- Name: flags flags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flags
    ADD CONSTRAINT flags_pkey PRIMARY KEY (id);


--
-- Name: fuel_station_flags fuel_station_flags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_station_flags
    ADD CONSTRAINT fuel_station_flags_pkey PRIMARY KEY (id);


--
-- Name: fuel_station_hours fuel_station_hours_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_station_hours
    ADD CONSTRAINT fuel_station_hours_pkey PRIMARY KEY (id);


--
-- Name: fuel_station_operating_periods fuel_station_operating_periods_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_station_operating_periods
    ADD CONSTRAINT fuel_station_operating_periods_pkey PRIMARY KEY (id);


--
-- Name: fuel_stations fuel_stations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_stations
    ADD CONSTRAINT fuel_stations_pkey PRIMARY KEY (id);


--
-- Name: fuel_types fuel_types_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_types
    ADD CONSTRAINT fuel_types_code_key UNIQUE (code);


--
-- Name: fuel_types fuel_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_types
    ADD CONSTRAINT fuel_types_pkey PRIMARY KEY (id);


--
-- Name: link_status link_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_status
    ADD CONSTRAINT link_status_pkey PRIMARY KEY (id);


--
-- Name: link_types link_types_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_types
    ADD CONSTRAINT link_types_code_key UNIQUE (code);


--
-- Name: link_types link_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_types
    ADD CONSTRAINT link_types_pkey PRIMARY KEY (id);


--
-- Name: links links_link_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.links
    ADD CONSTRAINT links_link_code_key UNIQUE (link_code);


--
-- Name: links links_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.links
    ADD CONSTRAINT links_pkey PRIMARY KEY (id);


--
-- Name: mileage_records mileage_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mileage_records
    ADD CONSTRAINT mileage_records_pkey PRIMARY KEY (id);


--
-- Name: model_versions model_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_pkey PRIMARY KEY (id);


--
-- Name: models models_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.models
    ADD CONSTRAINT models_pkey PRIMARY KEY (id);


--
-- Name: moment_contents moment_contents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_contents
    ADD CONSTRAINT moment_contents_pkey PRIMARY KEY (id);


--
-- Name: moment_descriptions moment_descriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_descriptions
    ADD CONSTRAINT moment_descriptions_pkey PRIMARY KEY (id);


--
-- Name: moment_reactions moment_reactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_reactions
    ADD CONSTRAINT moment_reactions_pkey PRIMARY KEY (id);


--
-- Name: moment_vehicles moment_vehicles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_vehicles
    ADD CONSTRAINT moment_vehicles_pkey PRIMARY KEY (id);


--
-- Name: moments moments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moments
    ADD CONSTRAINT moments_pkey PRIMARY KEY (id);


--
-- Name: odometers odometers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.odometers
    ADD CONSTRAINT odometers_pkey PRIMARY KEY (id);


--
-- Name: plate_types plate_types_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plate_types
    ADD CONSTRAINT plate_types_code_key UNIQUE (code);


--
-- Name: plate_types plate_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plate_types
    ADD CONSTRAINT plate_types_pkey PRIMARY KEY (id);


--
-- Name: plates plates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plates
    ADD CONSTRAINT plates_pkey PRIMARY KEY (id);


--
-- Name: station_fuel_prices station_fuel_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_fuel_prices
    ADD CONSTRAINT station_fuel_prices_pkey PRIMARY KEY (id);


--
-- Name: station_fuels station_fuels_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_fuels
    ADD CONSTRAINT station_fuels_pkey PRIMARY KEY (id);


--
-- Name: vehicle_claims vehicle_claims_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_claims
    ADD CONSTRAINT vehicle_claims_pkey PRIMARY KEY (id);


--
-- Name: vehicle_covers vehicle_covers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_covers
    ADD CONSTRAINT vehicle_covers_pkey PRIMARY KEY (id);


--
-- Name: vehicle_refuels vehicle_refuels_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_refuels
    ADD CONSTRAINT vehicle_refuels_pkey PRIMARY KEY (id);


--
-- Name: vehicles vehicles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_pkey PRIMARY KEY (id);


--
-- Name: vehicles vehicles_renavam_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_renavam_key UNIQUE (renavam);


--
-- Name: vehicles vehicles_vin_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_vin_key UNIQUE (vin);


--
-- Name: idx_actions_conversation; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_actions_conversation ON public.actions USING btree (conversation_id);


--
-- Name: idx_actions_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_actions_status ON public.actions USING btree (status);


--
-- Name: idx_actions_vehicle; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_actions_vehicle ON public.actions USING btree (vehicle_id);


--
-- Name: idx_colors_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_colors_active ON public.colors USING btree (active);


--
-- Name: idx_colors_color; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_colors_color ON public.colors USING btree (color);


--
-- Name: idx_colors_start_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_colors_start_date ON public.colors USING btree (start_date);


--
-- Name: idx_colors_vehicle_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_colors_vehicle_id ON public.colors USING btree (vehicle_id);


--
-- Name: idx_conversation_messages_conversation; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversation_messages_conversation ON public.conversation_messages USING btree (conversation_id);


--
-- Name: idx_conversations_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversations_code ON public.conversations USING btree (conversation_code);


--
-- Name: idx_conversations_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_conversations_status ON public.conversations USING btree (status);


--
-- Name: idx_entities_entity_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entities_entity_code ON public.entities USING btree (entity_code);


--
-- Name: idx_entities_legal_id_number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entities_legal_id_number ON public.entities USING btree (legal_id_number);


--
-- Name: idx_entity_documents_document_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entity_documents_document_type ON public.entity_documents USING btree (document_type);


--
-- Name: idx_entity_documents_entity_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entity_documents_entity_id ON public.entity_documents USING btree (entity_id);


--
-- Name: idx_entity_documents_entity_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entity_documents_entity_type ON public.entity_documents USING btree (entity_id, document_type);


--
-- Name: idx_entity_documents_file_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entity_documents_file_id ON public.entity_documents USING btree (file_id);


--
-- Name: idx_entity_documents_is_current; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entity_documents_is_current ON public.entity_documents USING btree (is_current);


--
-- Name: idx_files_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_files_status ON public.files USING btree (status);


--
-- Name: idx_files_uploaded_by_entity_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_files_uploaded_by_entity_id ON public.files USING btree (uploaded_by_entity_id);


--
-- Name: idx_files_vehicle_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_files_vehicle_id ON public.files USING btree (vehicle_id);


--
-- Name: idx_files_vehicle_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_files_vehicle_status ON public.files USING btree (vehicle_id, status);


--
-- Name: idx_links_entity_vehicle; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_links_entity_vehicle ON public.links USING btree (entity_id, vehicle_id);


--
-- Name: idx_links_link_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_links_link_code ON public.links USING btree (link_code);


--
-- Name: idx_links_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_links_status ON public.links USING btree (status);


--
-- Name: idx_mileage_records_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mileage_records_date ON public.mileage_records USING btree (recorded_at);


--
-- Name: idx_mileage_records_vehicle; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mileage_records_vehicle ON public.mileage_records USING btree (vehicle_id);


--
-- Name: idx_moment_contents_display_order; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_contents_display_order ON public.moment_contents USING btree (moment_id, display_order);


--
-- Name: idx_moment_contents_file_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_contents_file_id ON public.moment_contents USING btree (file_id);


--
-- Name: idx_moment_contents_moment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_contents_moment_id ON public.moment_contents USING btree (moment_id);


--
-- Name: idx_moment_descriptions_is_current; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_descriptions_is_current ON public.moment_descriptions USING btree (moment_id, is_current);


--
-- Name: idx_moment_descriptions_moment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_descriptions_moment_id ON public.moment_descriptions USING btree (moment_id);


--
-- Name: idx_moment_reactions_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_reactions_created_at ON public.moment_reactions USING btree (created_at);


--
-- Name: idx_moment_reactions_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_reactions_created_by ON public.moment_reactions USING btree (created_by_entity_id);


--
-- Name: idx_moment_reactions_moment_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_reactions_moment_created ON public.moment_reactions USING btree (moment_id, created_at);


--
-- Name: idx_moment_reactions_moment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_reactions_moment_id ON public.moment_reactions USING btree (moment_id);


--
-- Name: idx_moment_reactions_parent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_reactions_parent_id ON public.moment_reactions USING btree (parent_reaction_id);


--
-- Name: idx_moment_reactions_thread; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_reactions_thread ON public.moment_reactions USING btree (parent_reaction_id, created_at);


--
-- Name: idx_moment_vehicles_moment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_vehicles_moment_id ON public.moment_vehicles USING btree (moment_id);


--
-- Name: idx_moment_vehicles_vehicle_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moment_vehicles_vehicle_id ON public.moment_vehicles USING btree (vehicle_id);


--
-- Name: idx_moments_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moments_created_at ON public.moments USING btree (created_at);


--
-- Name: idx_moments_created_by_entity_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moments_created_by_entity_id ON public.moments USING btree (created_by_entity_id);


--
-- Name: idx_moments_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moments_status ON public.moments USING btree (status);


--
-- Name: idx_moments_visibility; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_moments_visibility ON public.moments USING btree (visibility);


--
-- Name: idx_plate_types_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plate_types_active ON public.plate_types USING btree (active);


--
-- Name: idx_plate_types_code; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plate_types_code ON public.plate_types USING btree (code);


--
-- Name: idx_plate_types_country; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plate_types_country ON public.plate_types USING btree (country);


--
-- Name: idx_plates_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plates_active ON public.plates USING btree (active);


--
-- Name: idx_plates_licensing_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plates_licensing_date ON public.plates USING btree (licensing_date);


--
-- Name: idx_plates_plate_number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plates_plate_number ON public.plates USING btree (plate_number);


--
-- Name: idx_plates_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plates_status ON public.plates USING btree (status);


--
-- Name: idx_plates_vehicle_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_plates_vehicle_id ON public.plates USING btree (vehicle_id);


--
-- Name: idx_vehicle_covers_file_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_covers_file_id ON public.vehicle_covers USING btree (file_id);


--
-- Name: idx_vehicle_covers_is_primary; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_covers_is_primary ON public.vehicle_covers USING btree (is_primary);


--
-- Name: idx_vehicle_covers_vehicle_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_covers_vehicle_id ON public.vehicle_covers USING btree (vehicle_id);


--
-- Name: idx_vehicle_covers_vehicle_primary; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_covers_vehicle_primary ON public.vehicle_covers USING btree (vehicle_id, is_primary);


--
-- Name: idx_vehicle_refuels_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_refuels_date ON public.vehicle_refuels USING btree (refuel_date);


--
-- Name: idx_vehicle_refuels_vehicle; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicle_refuels_vehicle ON public.vehicle_refuels USING btree (vehicle_id);


--
-- Name: idx_vehicles_current_plate; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicles_current_plate ON public.vehicles USING btree (current_plate);


--
-- Name: idx_vehicles_renavam; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicles_renavam ON public.vehicles USING btree (renavam);


--
-- Name: idx_vehicles_vin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vehicles_vin ON public.vehicles USING btree (vin);


--
-- Name: action_notes action_notes_action_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_notes
    ADD CONSTRAINT action_notes_action_id_fkey FOREIGN KEY (action_id) REFERENCES public.actions(id);


--
-- Name: action_notes action_notes_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_notes
    ADD CONSTRAINT action_notes_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id);


--
-- Name: action_status action_status_action_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_status
    ADD CONSTRAINT action_status_action_id_fkey FOREIGN KEY (action_id) REFERENCES public.actions(id);


--
-- Name: action_status action_status_changed_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_status
    ADD CONSTRAINT action_status_changed_by_entity_id_fkey FOREIGN KEY (changed_by_entity_id) REFERENCES public.entities(id);


--
-- Name: actions actions_action_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_action_type_id_fkey FOREIGN KEY (action_type_id) REFERENCES public.action_types(id);


--
-- Name: actions actions_assigned_to_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_assigned_to_entity_id_fkey FOREIGN KEY (assigned_to_entity_id) REFERENCES public.entities(id);


--
-- Name: actions actions_confirmed_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_confirmed_by_entity_id_fkey FOREIGN KEY (confirmed_by_entity_id) REFERENCES public.entities(id);


--
-- Name: actions actions_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id);


--
-- Name: actions actions_created_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_created_by_entity_id_fkey FOREIGN KEY (created_by_entity_id) REFERENCES public.entities(id);


--
-- Name: actions actions_created_by_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_created_by_link_id_fkey FOREIGN KEY (created_by_link_id) REFERENCES public.links(id);


--
-- Name: actions actions_depends_on_action_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_depends_on_action_id_fkey FOREIGN KEY (depends_on_action_id) REFERENCES public.actions(id);


--
-- Name: actions actions_executed_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_executed_by_entity_id_fkey FOREIGN KEY (executed_by_entity_id) REFERENCES public.entities(id);


--
-- Name: actions actions_executed_by_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_executed_by_link_id_fkey FOREIGN KEY (executed_by_link_id) REFERENCES public.links(id);


--
-- Name: actions actions_parent_action_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_parent_action_id_fkey FOREIGN KEY (parent_action_id) REFERENCES public.actions(id);


--
-- Name: actions actions_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: colors colors_created_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.colors
    ADD CONSTRAINT colors_created_by_entity_id_fkey FOREIGN KEY (created_by_entity_id) REFERENCES public.entities(id);


--
-- Name: colors colors_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.colors
    ADD CONSTRAINT colors_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: conversation_messages conversation_messages_action_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_messages
    ADD CONSTRAINT conversation_messages_action_id_fkey FOREIGN KEY (action_id) REFERENCES public.actions(id);


--
-- Name: conversation_messages conversation_messages_confirmed_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_messages
    ADD CONSTRAINT conversation_messages_confirmed_by_entity_id_fkey FOREIGN KEY (confirmed_by_entity_id) REFERENCES public.entities(id);


--
-- Name: conversation_messages conversation_messages_context_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_messages
    ADD CONSTRAINT conversation_messages_context_id_fkey FOREIGN KEY (context_id) REFERENCES public.conversation_contexts(id);


--
-- Name: conversation_messages conversation_messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_messages
    ADD CONSTRAINT conversation_messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id);


--
-- Name: conversation_messages conversation_messages_directed_to_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_messages
    ADD CONSTRAINT conversation_messages_directed_to_entity_id_fkey FOREIGN KEY (directed_to_entity_id) REFERENCES public.entities(id);


--
-- Name: conversation_messages conversation_messages_directed_to_participant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_messages
    ADD CONSTRAINT conversation_messages_directed_to_participant_id_fkey FOREIGN KEY (directed_to_participant_id) REFERENCES public.conversation_participants(id);


--
-- Name: conversation_messages conversation_messages_sender_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_messages
    ADD CONSTRAINT conversation_messages_sender_entity_id_fkey FOREIGN KEY (sender_entity_id) REFERENCES public.entities(id);


--
-- Name: conversation_messages conversation_messages_sender_participant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_messages
    ADD CONSTRAINT conversation_messages_sender_participant_id_fkey FOREIGN KEY (sender_participant_id) REFERENCES public.conversation_participants(id);


--
-- Name: conversation_participants conversation_participants_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(id);


--
-- Name: conversation_participants conversation_participants_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id);


--
-- Name: conversation_participants conversation_participants_invited_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_invited_by_entity_id_fkey FOREIGN KEY (invited_by_entity_id) REFERENCES public.entities(id);


--
-- Name: conversation_participants conversation_participants_invited_by_participant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_invited_by_participant_id_fkey FOREIGN KEY (invited_by_participant_id) REFERENCES public.conversation_participants(id);


--
-- Name: conversation_participants conversation_participants_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_link_id_fkey FOREIGN KEY (link_id) REFERENCES public.links(id);


--
-- Name: conversation_participants conversation_participants_removed_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversation_participants
    ADD CONSTRAINT conversation_participants_removed_by_entity_id_fkey FOREIGN KEY (removed_by_entity_id) REFERENCES public.entities(id);


--
-- Name: conversations conversations_main_context_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_main_context_id_fkey FOREIGN KEY (main_context_id) REFERENCES public.conversation_contexts(id);


--
-- Name: conversations conversations_primary_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_primary_vehicle_id_fkey FOREIGN KEY (primary_vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: entities entities_entity_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT entities_entity_type_id_fkey FOREIGN KEY (entity_type_id) REFERENCES public.entity_types(id);


--
-- Name: entity_documents entity_documents_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_documents
    ADD CONSTRAINT entity_documents_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id) ON DELETE CASCADE;


--
-- Name: entity_documents entity_documents_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_documents
    ADD CONSTRAINT entity_documents_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.files(id) ON DELETE CASCADE;


--
-- Name: entity_documents entity_documents_verified_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_documents
    ADD CONSTRAINT entity_documents_verified_by_entity_id_fkey FOREIGN KEY (verified_by_entity_id) REFERENCES public.entities(id);


--
-- Name: files files_uploaded_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_uploaded_by_entity_id_fkey FOREIGN KEY (uploaded_by_entity_id) REFERENCES public.entities(id);


--
-- Name: files files_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: fuel_station_flags fuel_station_flags_flag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_station_flags
    ADD CONSTRAINT fuel_station_flags_flag_id_fkey FOREIGN KEY (flag_id) REFERENCES public.flags(id);


--
-- Name: fuel_station_flags fuel_station_flags_registered_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_station_flags
    ADD CONSTRAINT fuel_station_flags_registered_by_entity_id_fkey FOREIGN KEY (registered_by_entity_id) REFERENCES public.entities(id);


--
-- Name: fuel_station_flags fuel_station_flags_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_station_flags
    ADD CONSTRAINT fuel_station_flags_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.fuel_stations(id);


--
-- Name: fuel_station_hours fuel_station_hours_registered_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_station_hours
    ADD CONSTRAINT fuel_station_hours_registered_by_entity_id_fkey FOREIGN KEY (registered_by_entity_id) REFERENCES public.entities(id);


--
-- Name: fuel_station_hours fuel_station_hours_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_station_hours
    ADD CONSTRAINT fuel_station_hours_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.fuel_stations(id);


--
-- Name: fuel_station_operating_periods fuel_station_operating_periods_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fuel_station_operating_periods
    ADD CONSTRAINT fuel_station_operating_periods_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.fuel_stations(id);


--
-- Name: link_status link_status_changed_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_status
    ADD CONSTRAINT link_status_changed_by_entity_id_fkey FOREIGN KEY (changed_by_entity_id) REFERENCES public.entities(id);


--
-- Name: link_status link_status_changed_by_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_status
    ADD CONSTRAINT link_status_changed_by_link_id_fkey FOREIGN KEY (changed_by_link_id) REFERENCES public.links(id);


--
-- Name: link_status link_status_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.link_status
    ADD CONSTRAINT link_status_link_id_fkey FOREIGN KEY (link_id) REFERENCES public.links(id);


--
-- Name: links links_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.links
    ADD CONSTRAINT links_entity_id_fkey FOREIGN KEY (entity_id) REFERENCES public.entities(id);


--
-- Name: links links_link_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.links
    ADD CONSTRAINT links_link_type_id_fkey FOREIGN KEY (link_type_id) REFERENCES public.link_types(id);


--
-- Name: links links_validated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.links
    ADD CONSTRAINT links_validated_by_fkey FOREIGN KEY (validated_by) REFERENCES public.links(id);


--
-- Name: links links_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.links
    ADD CONSTRAINT links_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: mileage_records mileage_records_odometer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mileage_records
    ADD CONSTRAINT mileage_records_odometer_id_fkey FOREIGN KEY (odometer_id) REFERENCES public.odometers(id);


--
-- Name: mileage_records mileage_records_registered_by_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mileage_records
    ADD CONSTRAINT mileage_records_registered_by_link_id_fkey FOREIGN KEY (registered_by_link_id) REFERENCES public.links(id);


--
-- Name: mileage_records mileage_records_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mileage_records
    ADD CONSTRAINT mileage_records_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: model_versions model_versions_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.model_versions
    ADD CONSTRAINT model_versions_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(id);


--
-- Name: models models_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.models
    ADD CONSTRAINT models_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.brands(id);


--
-- Name: moment_contents moment_contents_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_contents
    ADD CONSTRAINT moment_contents_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.files(id) ON DELETE CASCADE;


--
-- Name: moment_contents moment_contents_moment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_contents
    ADD CONSTRAINT moment_contents_moment_id_fkey FOREIGN KEY (moment_id) REFERENCES public.moments(id) ON DELETE CASCADE;


--
-- Name: moment_descriptions moment_descriptions_edited_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_descriptions
    ADD CONSTRAINT moment_descriptions_edited_by_entity_id_fkey FOREIGN KEY (edited_by_entity_id) REFERENCES public.entities(id);


--
-- Name: moment_descriptions moment_descriptions_moment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_descriptions
    ADD CONSTRAINT moment_descriptions_moment_id_fkey FOREIGN KEY (moment_id) REFERENCES public.moments(id) ON DELETE CASCADE;


--
-- Name: moment_reactions moment_reactions_created_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_reactions
    ADD CONSTRAINT moment_reactions_created_by_entity_id_fkey FOREIGN KEY (created_by_entity_id) REFERENCES public.entities(id);


--
-- Name: moment_reactions moment_reactions_moment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_reactions
    ADD CONSTRAINT moment_reactions_moment_id_fkey FOREIGN KEY (moment_id) REFERENCES public.moments(id) ON DELETE CASCADE;


--
-- Name: moment_reactions moment_reactions_parent_reaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_reactions
    ADD CONSTRAINT moment_reactions_parent_reaction_id_fkey FOREIGN KEY (parent_reaction_id) REFERENCES public.moment_reactions(id) ON DELETE CASCADE;


--
-- Name: moment_vehicles moment_vehicles_moment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_vehicles
    ADD CONSTRAINT moment_vehicles_moment_id_fkey FOREIGN KEY (moment_id) REFERENCES public.moments(id) ON DELETE CASCADE;


--
-- Name: moment_vehicles moment_vehicles_tagged_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_vehicles
    ADD CONSTRAINT moment_vehicles_tagged_by_entity_id_fkey FOREIGN KEY (tagged_by_entity_id) REFERENCES public.entities(id);


--
-- Name: moment_vehicles moment_vehicles_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moment_vehicles
    ADD CONSTRAINT moment_vehicles_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: moments moments_created_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moments
    ADD CONSTRAINT moments_created_by_entity_id_fkey FOREIGN KEY (created_by_entity_id) REFERENCES public.entities(id);


--
-- Name: odometers odometers_registered_by_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.odometers
    ADD CONSTRAINT odometers_registered_by_link_id_fkey FOREIGN KEY (registered_by_link_id) REFERENCES public.links(id);


--
-- Name: odometers odometers_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.odometers
    ADD CONSTRAINT odometers_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: plates plates_created_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plates
    ADD CONSTRAINT plates_created_by_entity_id_fkey FOREIGN KEY (created_by_entity_id) REFERENCES public.entities(id);


--
-- Name: plates plates_plate_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plates
    ADD CONSTRAINT plates_plate_type_id_fkey FOREIGN KEY (plate_type_id) REFERENCES public.plate_types(id);


--
-- Name: plates plates_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plates
    ADD CONSTRAINT plates_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: station_fuel_prices station_fuel_prices_reported_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_fuel_prices
    ADD CONSTRAINT station_fuel_prices_reported_by_entity_id_fkey FOREIGN KEY (reported_by_entity_id) REFERENCES public.entities(id);


--
-- Name: station_fuel_prices station_fuel_prices_station_fuel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_fuel_prices
    ADD CONSTRAINT station_fuel_prices_station_fuel_id_fkey FOREIGN KEY (station_fuel_id) REFERENCES public.station_fuels(id);


--
-- Name: station_fuel_prices station_fuel_prices_verified_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_fuel_prices
    ADD CONSTRAINT station_fuel_prices_verified_by_entity_id_fkey FOREIGN KEY (verified_by_entity_id) REFERENCES public.entities(id);


--
-- Name: station_fuels station_fuels_fuel_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_fuels
    ADD CONSTRAINT station_fuels_fuel_type_id_fkey FOREIGN KEY (fuel_type_id) REFERENCES public.fuel_types(id);


--
-- Name: station_fuels station_fuels_registered_by_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_fuels
    ADD CONSTRAINT station_fuels_registered_by_entity_id_fkey FOREIGN KEY (registered_by_entity_id) REFERENCES public.entities(id);


--
-- Name: station_fuels station_fuels_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.station_fuels
    ADD CONSTRAINT station_fuels_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.fuel_stations(id);


--
-- Name: vehicle_claims vehicle_claims_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_claims
    ADD CONSTRAINT vehicle_claims_link_id_fkey FOREIGN KEY (link_id) REFERENCES public.links(id);


--
-- Name: vehicle_claims vehicle_claims_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_claims
    ADD CONSTRAINT vehicle_claims_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: vehicle_covers vehicle_covers_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_covers
    ADD CONSTRAINT vehicle_covers_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.files(id) ON DELETE CASCADE;


--
-- Name: vehicle_covers vehicle_covers_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_covers
    ADD CONSTRAINT vehicle_covers_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: vehicle_refuels vehicle_refuels_fuel_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_refuels
    ADD CONSTRAINT vehicle_refuels_fuel_type_id_fkey FOREIGN KEY (fuel_type_id) REFERENCES public.fuel_types(id);


--
-- Name: vehicle_refuels vehicle_refuels_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_refuels
    ADD CONSTRAINT vehicle_refuels_link_id_fkey FOREIGN KEY (link_id) REFERENCES public.links(id);


--
-- Name: vehicle_refuels vehicle_refuels_registered_by_link_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_refuels
    ADD CONSTRAINT vehicle_refuels_registered_by_link_id_fkey FOREIGN KEY (registered_by_link_id) REFERENCES public.links(id);


--
-- Name: vehicle_refuels vehicle_refuels_station_fuel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_refuels
    ADD CONSTRAINT vehicle_refuels_station_fuel_id_fkey FOREIGN KEY (station_fuel_id) REFERENCES public.station_fuels(id);


--
-- Name: vehicle_refuels vehicle_refuels_station_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_refuels
    ADD CONSTRAINT vehicle_refuels_station_id_fkey FOREIGN KEY (station_id) REFERENCES public.fuel_stations(id);


--
-- Name: vehicle_refuels vehicle_refuels_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicle_refuels
    ADD CONSTRAINT vehicle_refuels_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: vehicles vehicles_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.brands(id);


--
-- Name: vehicles vehicles_model_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_model_id_fkey FOREIGN KEY (model_id) REFERENCES public.models(id);


--
-- Name: vehicles vehicles_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_version_id_fkey FOREIGN KEY (version_id) REFERENCES public.model_versions(id);


--
-- PostgreSQL database dump complete
--

\unrestrict z2F9fdzZ7yj5AMiiADaeubNCCDzPMPbvSbnEZy6UEReW97U0gdwldaAEHTugkjb

