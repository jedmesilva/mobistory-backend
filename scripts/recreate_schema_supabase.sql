-- =====================================================
-- RECREATE SCHEMA IGUAL AO SUPABASE
-- =====================================================

-- Dropar tudo
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Countries
CREATE TABLE countries (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  iso_code TEXT UNIQUE NOT NULL,
  iso3_code TEXT UNIQUE NOT NULL,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicle Brands
CREATE TABLE brands (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  brand TEXT NOT NULL,
  verified BOOLEAN DEFAULT false,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicle Models
CREATE TABLE models (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE RESTRICT,
  model TEXT NOT NULL,
  verified BOOLEAN DEFAULT false,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Model Versions
CREATE TABLE model_versions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  model_id UUID NOT NULL REFERENCES models(id) ON DELETE RESTRICT,
  version TEXT NOT NULL,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fuel Types
CREATE TABLE fuels (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT,
  description TEXT,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicle Categories
CREATE TABLE vehicle_categories (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  category TEXT NOT NULL,
  description TEXT,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Plate Types
CREATE TABLE plate_types (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  country_id UUID NOT NULL REFERENCES countries(id) ON DELETE RESTRICT,
  name TEXT NOT NULL,
  description TEXT,
  format_pattern TEXT,
  valid_from DATE,
  valid_until DATE,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicles
CREATE TABLE vehicles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE RESTRICT,
  model_id UUID NOT NULL REFERENCES models(id) ON DELETE RESTRICT,
  version_id UUID REFERENCES model_versions(id) ON DELETE SET NULL,
  category_id UUID NOT NULL REFERENCES vehicle_categories(id) ON DELETE RESTRICT,
  chassis TEXT UNIQUE NOT NULL,
  model_year INTEGER NOT NULL,
  manufacture_year INTEGER NOT NULL,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT valid_years CHECK (manufacture_year <= model_year)
);

-- Vehicle Registrations
CREATE TABLE vehicle_registrations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  country_id UUID NOT NULL REFERENCES countries(id) ON DELETE RESTRICT,
  registration_number TEXT NOT NULL,
  registration_type TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicle Plates
CREATE TABLE plates (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  plate_type_id UUID NOT NULL REFERENCES plate_types(id) ON DELETE RESTRICT,
  plate TEXT NOT NULL,
  state TEXT,
  licensing_country_id UUID NOT NULL REFERENCES countries(id) ON DELETE RESTRICT,
  start_date DATE NOT NULL,
  end_date DATE,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicle Colors
CREATE TABLE colors (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  color TEXT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicle Fuels
CREATE TABLE vehicle_fuels (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  fuel_id UUID NOT NULL REFERENCES fuels(id) ON DELETE RESTRICT,
  start_date DATE NOT NULL,
  end_date DATE,
  active BOOLEAN DEFAULT true,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Entities
CREATE TABLE entities (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  entity_type TEXT NOT NULL CHECK (entity_type IN ('person', 'ai_agent', 'iot_device', 'organization', 'robot')),
  name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  document_number TEXT,
  ai_model TEXT,
  ai_capabilities JSONB,
  device_serial TEXT,
  device_type TEXT,
  legal_id TEXT,
  organization_type TEXT,
  metadata JSONB,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicle Entity Links
CREATE TABLE vehicle_entity_links (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  relationship_type TEXT NOT NULL CHECK (relationship_type IN (
    'owner', 'co_owner', 'renter', 'authorized_driver',
    'ai_assistant', 'monitoring_device', 'maintenance_robot',
    'fleet_manager', 'emergency_contact', 'insurance_company'
  )),
  permissions JSONB DEFAULT '{}'::jsonb,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'terminated', 'pending')),
  start_date DATE NOT NULL,
  end_date DATE,
  notes TEXT,
  created_by UUID REFERENCES entities(id),
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_active_link UNIQUE(vehicle_id, entity_id, relationship_type, start_date)
);

-- Conversations
CREATE TABLE conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  title TEXT,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
  last_message_at TIMESTAMPTZ,
  last_message_preview TEXT,
  unread_count INTEGER DEFAULT 0,
  metadata JSONB DEFAULT '{}'::jsonb,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_entity_vehicle_conversation UNIQUE(vehicle_id, entity_id)
);

-- Messages
CREATE TABLE messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  sender_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  message_type TEXT NOT NULL DEFAULT 'text' CHECK (message_type IN (
    'text', 'image', 'video', 'audio', 'file', 'location', 'system'
  )),
  content TEXT,
  media_urls JSONB DEFAULT '[]'::jsonb,
  metadata JSONB DEFAULT '{}'::jsonb,
  status TEXT NOT NULL DEFAULT 'sent' CHECK (status IN (
    'sending', 'sent', 'delivered', 'read', 'failed'
  )),
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  delivered_at TIMESTAMPTZ,
  read_at TIMESTAMPTZ,
  reply_to_message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
  reactions JSONB DEFAULT '[]'::jsonb,
  edited BOOLEAN DEFAULT false,
  edited_at TIMESTAMPTZ,
  deleted BOOLEAN DEFAULT false,
  deleted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Moments
CREATE TABLE moments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  caption TEXT,
  type TEXT NOT NULL CHECK (type IN ('image', 'video', 'text')),
  location TEXT,
  tags JSONB DEFAULT '[]'::jsonb,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Moment Images
CREATE TABLE moment_images (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  moment_id UUID NOT NULL REFERENCES moments(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  image_order INTEGER DEFAULT 0,
  width INTEGER,
  height INTEGER,
  size_bytes INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Moment Reactions
CREATE TABLE moment_reactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  moment_id UUID NOT NULL REFERENCES moments(id) ON DELETE CASCADE,
  entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  reaction_type TEXT NOT NULL DEFAULT 'like' CHECK (reaction_type IN ('like', 'love', 'care', 'wow', 'sad', 'angry')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_reaction_per_entity UNIQUE(moment_id, entity_id)
);

-- Moment Comments
CREATE TABLE moment_comments (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  moment_id UUID NOT NULL REFERENCES moments(id) ON DELETE CASCADE,
  entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  comment TEXT NOT NULL,
  parent_comment_id UUID REFERENCES moment_comments(id) ON DELETE CASCADE,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vehicle Images
CREATE TABLE vehicle_images (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  vehicle_id UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  is_primary BOOLEAN DEFAULT false,
  width INTEGER,
  height INTEGER,
  size_bytes INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_vehicles_chassis ON vehicles(chassis);
CREATE INDEX idx_plates_plate ON plates(plate);
CREATE INDEX idx_plates_vehicle_id ON plates(vehicle_id);
CREATE INDEX idx_colors_vehicle_id ON colors(vehicle_id);
CREATE INDEX idx_vehicle_fuels_vehicle_id ON vehicle_fuels(vehicle_id);
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_email ON entities(email) WHERE email IS NOT NULL;
CREATE INDEX idx_vehicle_links_vehicle ON vehicle_entity_links(vehicle_id);
CREATE INDEX idx_vehicle_links_entity ON vehicle_entity_links(entity_id);
CREATE INDEX idx_conversations_vehicle ON conversations(vehicle_id);
CREATE INDEX idx_conversations_entity ON conversations(entity_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_moments_vehicle ON moments(vehicle_id);
CREATE INDEX idx_moment_images_moment ON moment_images(moment_id);
CREATE INDEX idx_vehicle_images_vehicle ON vehicle_images(vehicle_id);

-- Unique Constraints
CREATE UNIQUE INDEX idx_plates_active_unique ON plates(vehicle_id) WHERE active = true;
CREATE UNIQUE INDEX idx_colors_active_unique ON colors(vehicle_id) WHERE active = true;

-- Triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_entities_updated_at BEFORE UPDATE ON entities FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vehicle_links_updated_at BEFORE UPDATE ON vehicle_entity_links FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_moments_updated_at BEFORE UPDATE ON moments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_moment_comments_updated_at BEFORE UPDATE ON moment_comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
