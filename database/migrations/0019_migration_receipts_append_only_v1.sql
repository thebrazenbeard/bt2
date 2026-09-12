-- Migration receipts are durable evidence, not mutable current-state rows.
-- Corrections/supersession must be represented by a new receipt so failed and
-- historical attempts remain auditable.

CREATE OR REPLACE FUNCTION bt2.reject_migration_receipt_mutation_v1()
RETURNS trigger
LANGUAGE plpgsql
AS $function$
BEGIN
  RAISE EXCEPTION 'MIGRATION_RECEIPTS_ARE_APPEND_ONLY';
END
$function$;

DROP TRIGGER IF EXISTS migration_receipts_no_update_delete_v1 ON bt2.migration_receipts;
CREATE TRIGGER migration_receipts_no_update_delete_v1
BEFORE UPDATE OR DELETE ON bt2.migration_receipts
FOR EACH ROW EXECUTE FUNCTION bt2.reject_migration_receipt_mutation_v1();
