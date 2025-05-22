-- Create enums
CREATE TYPE club_sport_type AS ENUM (
  'football',
  'tennis',
  'basketball',
  'volleyball',
  'hockey',
  'handball',
  'rugby',
  'baseball',
  'cricket',
  'golf',
  'athletics',
  'swimming',
  'cycling',
  'martial_arts',
  'table_tennis',
  'badminton',
  'padel',
  'other'
);

CREATE TYPE event_type AS ENUM (
  'match',
  'tournament',
  'training',
  'friendly_match',
  'championship',
  'cup',
  'other'
);

CREATE TYPE event_status AS ENUM (
  'scheduled',
  'canceled',
  'postponed',
  'in_progress',
  'completed',
  'live_stream'
);

CREATE TYPE ticket_type AS ENUM (
  'standard',
  'vip',
  'season_pass',
  'stream_access',
  'stream_donation',
  'club_donation'
);

CREATE TYPE ticket_status AS ENUM (
  'active',
  'used',
  'expired',
  'canceled',
  'refunded'
);

CREATE TYPE club_package_type AS ENUM (
  'basic',
  'tickets',
  'streaming',
  'premium',
  'all_inclusive'
);

-- Create tables
CREATE TABLE IF NOT EXISTS clubs (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  founded_year INTEGER,
  sport_type club_sport_type NOT NULL,
  logo VARCHAR(255),
  banner VARCHAR(255),
  color_primary VARCHAR(10),
  color_secondary VARCHAR(10),
  address TEXT,
  city VARCHAR(100),
  region VARCHAR(100),
  country VARCHAR(100) DEFAULT 'Czech Republic',
  website VARCHAR(255),
  email VARCHAR(255),
  phone VARCHAR(100),
  social_media JSONB,
  membership_info TEXT,
  is_verified BOOLEAN DEFAULT FALSE,
  fitness_tokens_balance INTEGER DEFAULT 0,
  stripe_account_id VARCHAR(255),
  active_package club_package_type DEFAULT 'basic',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS club_managers (
  id SERIAL PRIMARY KEY,
  club_id INTEGER NOT NULL REFERENCES clubs(id),
  user_id INTEGER NOT NULL REFERENCES users(id),
  role VARCHAR(50) DEFAULT 'admin',
  permissions JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS club_seasons (
  id SERIAL PRIMARY KEY,
  club_id INTEGER NOT NULL REFERENCES clubs(id),
  name VARCHAR(255) NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS club_events (
  id SERIAL PRIMARY KEY,
  club_id INTEGER NOT NULL REFERENCES clubs(id),
  season_id INTEGER REFERENCES club_seasons(id),
  title VARCHAR(255) NOT NULL,
  event_type event_type NOT NULL,
  opponent VARCHAR(255),
  location VARCHAR(255),
  venue_address TEXT,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  description TEXT,
  banner_image VARCHAR(255),
  status event_status DEFAULT 'scheduled',
  result VARCHAR(100),
  event_details JSONB,
  has_tickets BOOLEAN DEFAULT FALSE,
  has_stream BOOLEAN DEFAULT FALSE,
  stream_url VARCHAR(255),
  stream_key VARCHAR(255),
  stream_price INTEGER,
  ticket_price INTEGER,
  tickets_available INTEGER,
  tickets_sold INTEGER DEFAULT 0,
  allow_donations BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS event_ticket_types (
  id SERIAL PRIMARY KEY,
  event_id INTEGER NOT NULL REFERENCES club_events(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price INTEGER NOT NULL,
  fitness_tokens_price INTEGER,
  quantity_available INTEGER NOT NULL,
  quantity_sold INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  ticket_type ticket_type DEFAULT 'standard',
  benefits JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS event_tickets (
  id SERIAL PRIMARY KEY,
  ticket_type_id INTEGER NOT NULL REFERENCES event_ticket_types(id),
  event_id INTEGER NOT NULL REFERENCES club_events(id),
  user_id INTEGER REFERENCES users(id),
  purchaser_name VARCHAR(255),
  purchaser_email VARCHAR(255),
  purchaser_phone VARCHAR(50),
  ticket_number VARCHAR(50) NOT NULL UNIQUE,
  price_paid INTEGER NOT NULL,
  payment_method VARCHAR(50),
  payment_id VARCHAR(255),
  status ticket_status DEFAULT 'active',
  check_in_time TIMESTAMP,
  qr_code VARCHAR(255),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stream_accesses (
  id SERIAL PRIMARY KEY,
  event_id INTEGER NOT NULL REFERENCES club_events(id),
  user_id INTEGER REFERENCES users(id),
  purchaser_name VARCHAR(255),
  purchaser_email VARCHAR(255),
  access_code VARCHAR(50) NOT NULL UNIQUE,
  price_paid INTEGER,
  is_donation BOOLEAN DEFAULT FALSE,
  payment_method VARCHAR(50),
  payment_id VARCHAR(255),
  status ticket_status DEFAULT 'active',
  access_start TIMESTAMP DEFAULT NOW(),
  access_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS club_packages (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  package_type club_package_type NOT NULL,
  description TEXT,
  features JSONB,
  price_monthly INTEGER,
  price_yearly INTEGER,
  fitness_tokens_price INTEGER,
  ticket_commission_percentage DECIMAL(5, 2),
  stream_commission_percentage DECIMAL(5, 2),
  max_events_per_month INTEGER,
  max_tickets_per_event INTEGER,
  max_streams_per_month INTEGER,
  includes_marketing BOOLEAN DEFAULT FALSE,
  includes_analytics BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS club_subscriptions (
  id SERIAL PRIMARY KEY,
  club_id INTEGER NOT NULL REFERENCES clubs(id),
  package_id INTEGER NOT NULL REFERENCES club_packages(id),
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP,
  price_paid INTEGER NOT NULL,
  payment_method VARCHAR(50),
  payment_id VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  auto_renew BOOLEAN DEFAULT FALSE,
  stripe_subscription_id VARCHAR(255),
  fitness_tokens_used INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS club_event_stats (
  id SERIAL PRIMARY KEY,
  event_id INTEGER NOT NULL REFERENCES club_events(id),
  club_id INTEGER NOT NULL REFERENCES clubs(id),
  total_revenue INTEGER DEFAULT 0,
  ticket_revenue INTEGER DEFAULT 0,
  stream_revenue INTEGER DEFAULT 0,
  donation_revenue INTEGER DEFAULT 0,
  attendance_count INTEGER DEFAULT 0,
  stream_views INTEGER DEFAULT 0,
  stream_unique_viewers INTEGER DEFAULT 0,
  stream_average_watch_time INTEGER,
  sportmatch_commission INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS club_templates (
  id SERIAL PRIMARY KEY,
  club_id INTEGER NOT NULL REFERENCES clubs(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  template_type VARCHAR(50) NOT NULL,
  template_data JSONB NOT NULL,
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Add default package
INSERT INTO club_packages (name, package_type, description, price_monthly, features, max_events_per_month, is_active)
VALUES ('Basic', 'basic', 'Basic package for clubs', 0, '["Basic club profile", "Event creation"]', 10, true);