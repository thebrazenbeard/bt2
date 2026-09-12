-- BT2 internal service-boundary hardening V1.
-- ADMIN-ONLY: WoWSQL MCP SQL safety blocks REVOKE; apply only through an authorized admin route.
-- Canonical and legacy schemas are internal control-plane data, not implicit PostgREST surfaces.
-- Source owner: Two under BT2-CANONICAL-PLATFORM-20260910.

REVOKE ALL ON SCHEMA bt2 FROM PUBLIC;
REVOKE ALL ON SCHEMA bt2_legacy FROM PUBLIC;
REVOKE ALL ON SCHEMA bt2 FROM anon, authenticated, service_role;
REVOKE ALL ON SCHEMA bt2_legacy FROM anon, authenticated, service_role;

REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA bt2 FROM PUBLIC, anon, authenticated, service_role;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA bt2_legacy FROM PUBLIC, anon, authenticated, service_role;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA bt2 FROM PUBLIC, anon, authenticated, service_role;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA bt2_legacy FROM PUBLIC, anon, authenticated, service_role;
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA bt2 FROM PUBLIC, anon, authenticated, service_role;
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA bt2_legacy FROM PUBLIC, anon, authenticated, service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA bt2 REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA bt2_legacy REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA bt2 REVOKE ALL ON SEQUENCES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA bt2_legacy REVOKE ALL ON SEQUENCES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA bt2 REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA bt2_legacy REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- Any future client/API exposure must be a separate reviewed grant/projection.
