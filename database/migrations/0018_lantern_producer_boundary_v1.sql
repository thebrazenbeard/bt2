-- Preserve a narrow governed-material producer boundary on provider-neutral PostgreSQL.
-- This migration grants no producer permit and creates no material rows.

ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text)
  OWNER TO CURRENT_USER;

ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text)
  SECURITY DEFINER;

ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text)
  SET search_path TO pg_catalog, bt2, pg_temp;

REVOKE ALL ON FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text) TO CURRENT_USER;
