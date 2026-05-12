-- InternFlow – PostgreSQL initialisation script
-- Runs once when the container is first created.
-- Alembic manages the actual schema; this file sets up extensions and roles.

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for future full-text search on candidate names/emails
CREATE EXTENSION IF NOT EXISTS pg_trgm;
