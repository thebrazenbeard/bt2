-- Migration receipts are durable migration evidence and must be append-only.
-- Corrections are represented by new versioned receipts, never in-place mutation.

BEGIN;

INSERT INTO bt2.migration_receipts(
  migration_key,source_system,target_component,migration_digest_sha256,
  result_state,evidence,applied_at,verified_at
) VALUES (
  'BT2-CI-APPEND-ONLY-RECEIPT-V1','CI','CI',repeat('a',64),
  'VERIFIED','{"version":1}'::jsonb,clock_timestamp(),clock_timestamp()
);

DO $test$
DECLARE v_update_rejected boolean:=false; v_delete_rejected boolean:=false;
BEGIN
  BEGIN
    UPDATE bt2.migration_receipts
    SET evidence='{"version":999}'::jsonb
    WHERE migration_key='BT2-CI-APPEND-ONLY-RECEIPT-V1';
  EXCEPTION WHEN OTHERS THEN
    IF position('MIGRATION_RECEIPTS_ARE_APPEND_ONLY' in SQLERRM)>0 THEN
      v_update_rejected:=true;
    ELSE
      RAISE;
    END IF;
  END;
  IF NOT v_update_rejected THEN
    RAISE EXCEPTION 'MIGRATION_RECEIPT_UPDATE_WAS_ACCEPTED';
  END IF;

  BEGIN
    DELETE FROM bt2.migration_receipts
    WHERE migration_key='BT2-CI-APPEND-ONLY-RECEIPT-V1';
  EXCEPTION WHEN OTHERS THEN
    IF position('MIGRATION_RECEIPTS_ARE_APPEND_ONLY' in SQLERRM)>0 THEN
      v_delete_rejected:=true;
    ELSE
      RAISE;
    END IF;
  END;
  IF NOT v_delete_rejected THEN
    RAISE EXCEPTION 'MIGRATION_RECEIPT_DELETE_WAS_ACCEPTED';
  END IF;
END
$test$;

-- A correction/successor remains legal as a new immutable receipt.
INSERT INTO bt2.migration_receipts(
  migration_key,source_system,target_component,migration_digest_sha256,
  result_state,evidence,applied_at,verified_at
) VALUES (
  'BT2-CI-APPEND-ONLY-RECEIPT-V2','CI','CI',repeat('b',64),
  'VERIFIED','{"version":2,"supersedes":"BT2-CI-APPEND-ONLY-RECEIPT-V1"}'::jsonb,
  clock_timestamp(),clock_timestamp()
);

DO $test$
BEGIN
  IF (SELECT count(*) FROM bt2.migration_receipts
      WHERE migration_key IN ('BT2-CI-APPEND-ONLY-RECEIPT-V1','BT2-CI-APPEND-ONLY-RECEIPT-V2'))<>2 THEN
    RAISE EXCEPTION 'APPEND_ONLY_SUCCESSOR_RECEIPT_NOT_PRESERVED';
  END IF;
END
$test$;

ROLLBACK;
