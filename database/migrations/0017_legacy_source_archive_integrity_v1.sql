-- BT2 legacy source archive integrity V1.
-- Preserves historical source rows without activating their semantics.

CREATE OR REPLACE FUNCTION bt2_legacy.reject_source_row_mutation_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
BEGIN
  RAISE EXCEPTION 'APPEND_ONLY_LEGACY_SOURCE_HISTORY';
END
$function$;

DROP TRIGGER IF EXISTS source_rows_append_only_v1 ON bt2_legacy.source_rows;
CREATE TRIGGER source_rows_append_only_v1
BEFORE UPDATE OR DELETE ON bt2_legacy.source_rows
FOR EACH ROW EXECUTE FUNCTION bt2_legacy.reject_source_row_mutation_v1();

CREATE OR REPLACE FUNCTION bt2.register_legacy_source_snapshot_v1(
  p_source_kind text,
  p_source_name text,
  p_canonical_locator text,
  p_source_ref text,
  p_source_commit text,
  p_visibility text,
  p_evidence_class text,
  p_metadata jsonb
)
RETURNS uuid
LANGUAGE plpgsql
AS $function$
DECLARE
  v_id uuid;
  v_existing record;
BEGIN
  IF p_source_kind IS NULL OR btrim(p_source_kind)='' OR
     p_source_name IS NULL OR btrim(p_source_name)='' OR
     p_canonical_locator IS NULL OR btrim(p_canonical_locator)='' OR
     p_source_ref IS NULL OR btrim(p_source_ref)='' OR
     p_source_commit IS NULL OR btrim(p_source_commit)='' THEN
    RAISE EXCEPTION 'INVALID_LEGACY_SOURCE_SNAPSHOT_IDENTITY';
  END IF;

  IF coalesce(p_metadata->>'classification','') <> 'HISTORICAL_PROVENANCE_ONLY' THEN
    RAISE EXCEPTION 'LEGACY_SOURCE_SNAPSHOT_MUST_BE_HISTORICAL_ONLY';
  END IF;

  SELECT * INTO v_existing
  FROM bt2.source_snapshots s
  WHERE s.source_kind=p_source_kind
    AND s.source_name=p_source_name
    AND s.source_ref=p_source_ref
    AND s.source_commit=p_source_commit;

  IF FOUND THEN
    IF v_existing.canonical_locator IS DISTINCT FROM p_canonical_locator
       OR v_existing.visibility IS DISTINCT FROM p_visibility
       OR v_existing.evidence_class IS DISTINCT FROM p_evidence_class
       OR v_existing.metadata IS DISTINCT FROM p_metadata THEN
      RAISE EXCEPTION 'LEGACY_SOURCE_SNAPSHOT_REPLAY_CONFLICT';
    END IF;
    RETURN v_existing.source_snapshot_id;
  END IF;

  INSERT INTO bt2.source_snapshots(
    source_snapshot_id,source_kind,source_name,canonical_locator,source_ref,
    source_commit,source_tree,visibility,captured_at,evidence_class,metadata
  ) VALUES(
    gen_random_uuid(),p_source_kind,p_source_name,p_canonical_locator,p_source_ref,
    p_source_commit,NULL,p_visibility,clock_timestamp(),p_evidence_class,p_metadata
  )
  RETURNING source_snapshot_id INTO v_id;

  RETURN v_id;
END
$function$;

CREATE OR REPLACE FUNCTION bt2.import_legacy_source_rows_v1(
  p_source_snapshot_id uuid,
  p_source_system text,
  p_rows jsonb
)
RETURNS integer
LANGUAGE plpgsql
AS $function$
DECLARE
  v_snapshot record;
  v_elem jsonb;
  v_schema text;
  v_relation text;
  v_primary_key text;
  v_row_data jsonb;
  v_existing record;
  v_inserted integer := 0;
BEGIN
  SELECT * INTO STRICT v_snapshot
  FROM bt2.source_snapshots
  WHERE source_snapshot_id=p_source_snapshot_id;

  IF coalesce(v_snapshot.metadata->>'classification','') <> 'HISTORICAL_PROVENANCE_ONLY' THEN
    RAISE EXCEPTION 'LEGACY_SOURCE_IMPORT_REQUIRES_HISTORICAL_SNAPSHOT';
  END IF;

  IF p_source_system IS NULL OR btrim(p_source_system)='' THEN
    RAISE EXCEPTION 'INVALID_LEGACY_SOURCE_SYSTEM';
  END IF;

  IF jsonb_typeof(p_rows) <> 'array' THEN
    RAISE EXCEPTION 'LEGACY_SOURCE_ROWS_MUST_BE_ARRAY';
  END IF;

  FOR v_elem IN SELECT value FROM jsonb_array_elements(p_rows)
  LOOP
    IF jsonb_typeof(v_elem) <> 'object'
       OR (SELECT array_agg(k ORDER BY k) FROM jsonb_object_keys(v_elem) k)
          IS DISTINCT FROM ARRAY['row_data','source_primary_key','source_relation','source_schema']::text[] THEN
      RAISE EXCEPTION 'INVALID_LEGACY_SOURCE_ROW_ENVELOPE';
    END IF;

    v_schema := v_elem->>'source_schema';
    v_relation := v_elem->>'source_relation';
    v_primary_key := v_elem->>'source_primary_key';
    v_row_data := v_elem->'row_data';

    IF v_schema IS NULL OR btrim(v_schema)=''
       OR v_relation IS NULL OR btrim(v_relation)=''
       OR v_primary_key IS NULL OR btrim(v_primary_key)=''
       OR jsonb_typeof(v_row_data) <> 'object' THEN
      RAISE EXCEPTION 'INVALID_LEGACY_SOURCE_ROW_FIELDS';
    END IF;

    SELECT * INTO v_existing
    FROM bt2_legacy.source_rows r
    WHERE r.source_system=p_source_system
      AND r.source_schema=v_schema
      AND r.source_relation=v_relation
      AND r.source_primary_key=v_primary_key;

    IF FOUND THEN
      IF v_existing.row_data IS DISTINCT FROM v_row_data
         OR v_existing.source_snapshot_id IS DISTINCT FROM p_source_snapshot_id THEN
        RAISE EXCEPTION 'LEGACY_SOURCE_ROW_REPLAY_CONFLICT:%:%:%',v_schema,v_relation,v_primary_key;
      END IF;
      CONTINUE;
    END IF;

    INSERT INTO bt2_legacy.source_rows(
      source_row_id,source_system,source_schema,source_relation,
      source_primary_key,row_data,source_snapshot_id,captured_at
    ) VALUES(
      gen_random_uuid(),p_source_system,v_schema,v_relation,
      v_primary_key,v_row_data,p_source_snapshot_id,clock_timestamp()
    );
    v_inserted := v_inserted + 1;
  END LOOP;

  RETURN v_inserted;
END
$function$;
