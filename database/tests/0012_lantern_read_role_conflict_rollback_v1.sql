-- PostgreSQL 16+ / opt-in / isolated database only.
-- Run AFTER the canonical BT2 V4 migration through 0024 as its migration
-- owner, with CREATEROLE (and authority to SET ROLE) in a disposable cluster.
-- The script intentionally demonstrates that the existing direct `bt2` reader
-- route cannot satisfy BOTH least-privilege and the BT2 access assertion.
-- It does not install or qualify a replacement API. All changes roll back.

BEGIN;

CREATE ROLE bt2_lantern_role_falsifier_v1
  LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

-- PostgreSQL 16+ does not implicitly grant the CREATEROLE caller the SET
-- option on the role it creates. Explicitly authorize this rollback-only
-- impersonation test; neither the role nor membership survives ROLLBACK.
GRANT bt2_lantern_role_falsifier_v1 TO CURRENT_USER
  WITH SET TRUE, INHERIT FALSE;

-- A reader granted direct facade usage must be rejected by the BT2 assertion.
GRANT USAGE ON SCHEMA bt2 TO bt2_lantern_role_falsifier_v1;
GRANT EXECUTE ON FUNCTION bt2.material_cut_v1(text)
  TO bt2_lantern_role_falsifier_v1;

DO $assert_conflict$
DECLARE
  v_expected_error constant text :=
    'BT2_INTERNAL_SCHEMA_EXPOSED_TO_ROLE:bt2_lantern_role_falsifier_v1';
  v_observed text;
BEGIN
  BEGIN
    PERFORM bt2.assert_internal_access_boundary_v1();
  EXCEPTION WHEN OTHERS THEN
    GET STACKED DIAGNOSTICS v_observed = MESSAGE_TEXT;
  END;
  IF v_observed IS DISTINCT FROM v_expected_error THEN
    RAISE EXCEPTION 'BT2_READER_CONFLICT_EXPECTED_BOUNDARY_FAILURE:got=%',
      coalesce(v_observed, 'NONE');
  END IF;
END
$assert_conflict$;

-- Undo the forbidden grant; the BT2 boundary is restored, but a reader can no
-- longer resolve the direct bt2 facade or internal runtime-visible view.
REVOKE USAGE ON SCHEMA bt2 FROM bt2_lantern_role_falsifier_v1;
REVOKE EXECUTE ON FUNCTION bt2.material_cut_v1(text)
  FROM bt2_lantern_role_falsifier_v1;

DO $assert_boundary_restored$
BEGIN
  PERFORM bt2.assert_internal_access_boundary_v1();
  IF has_schema_privilege('bt2_lantern_role_falsifier_v1','bt2','USAGE') THEN
    RAISE EXCEPTION 'BT2_READER_CONFLICT_UNEXPECTED_INTERNAL_USAGE';
  END IF;
END
$assert_boundary_restored$;

SET LOCAL ROLE bt2_lantern_role_falsifier_v1;

DO $assert_direct_denial$
DECLARE
  v_denied boolean := false;
BEGIN
  IF current_user <> 'bt2_lantern_role_falsifier_v1' THEN
    RAISE EXCEPTION 'BT2_READER_CONFLICT_ROLE_SWITCH_FAILED:%', current_user;
  END IF;
  IF has_schema_privilege(current_user, 'bt2', 'USAGE') THEN
    RAISE EXCEPTION 'BT2_READER_CONFLICT_ROLE_HAS_INTERNAL_USAGE';
  END IF;
  BEGIN
    PERFORM * FROM bt2.material_cut_v1('PROJECT_LANTERN');
  EXCEPTION WHEN insufficient_privilege THEN
    v_denied := true;
  END;
  IF NOT v_denied THEN
    RAISE EXCEPTION 'BT2_READER_CONFLICT_DIRECT_CUT_NOT_DENIED';
  END IF;
END
$assert_direct_denial$;

RESET ROLE;
ROLLBACK;
