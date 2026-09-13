-- Harden the Lantern SECURITY DEFINER search path against caller temp-schema shadowing.
-- Forward migration for installations that already applied 0018.

ALTER FUNCTION bt2.append_material_v1(uuid,text,text,text,text,text)
  SET search_path TO pg_catalog, bt2, pg_temp;
