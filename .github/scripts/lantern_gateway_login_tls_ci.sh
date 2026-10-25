#!/usr/bin/env bash
# Disposable workflow-only qualification for the uninstalled Lantern read gateway.
# Requires a freshly rebuilt BT2 PostgreSQL 16/17 service container.
# `preflight` runs before the gateway candidate; `reader` runs after it.
set -euo pipefail

phase="${1:-}"
case "$phase" in
  preflight|reader) ;;
  *) echo 'usage: run_lantern_gateway_login_tls_ci.sh preflight|reader' >&2; exit 2 ;;
esac
: "${DATABASE_URL:?missing disposable migration-owner DSN}"
: "${POSTGRES_CONTAINER_ID:?missing disposable PostgreSQL container ID}"
: "${RUNNER_TEMP:?missing isolated runner temp directory}"
: "${BT2_CI_TLS_ADMIN_DSN:?missing disposable PostgreSQL superuser DSN}"
: "${BT2_CI_PG_MAJOR:?missing pinned PostgreSQL major}"

reader_role='bt2_lantern_gateway_reader_v1'
owner_role='bt2_lantern_gateway_owner_v1'
intruder_role='bt2_lantern_gateway_intruder_ci'

if [[ "$phase" == 'preflight' ]]; then
  # Falsifier: a third-party LOGIN with SET membership in the NOLOGIN
  # SECURITY DEFINER owner would acquire its internal bt2 relation grants.
  # The gateway installer must reject this even though the migration caller
  # legitimately has SET membership for the ownership handoff.
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c \
    "CREATE ROLE $intruder_role LOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS"
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c \
    "GRANT $owner_role TO $intruder_role WITH SET TRUE, INHERIT FALSE"

  cleanup_intruder() {
    psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c \
      "REVOKE $owner_role FROM $intruder_role" >/dev/null
    psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c \
      "DROP ROLE $intruder_role" >/dev/null
  }
  trap cleanup_intruder EXIT

  if installer_result="$(psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
      -f native/project/lantern_read_gateway_v1_candidate.sql 2>&1)"; then
    echo 'FAIL: gateway accepted external inbound SECURITY DEFINER owner member' >&2
    exit 1
  fi
  if [[ "$installer_result" != *'LANTERN_GATEWAY_ROLE_MEMBERSHIP_NOT_ISOLATED'* ]]; then
    echo 'FAIL: gateway rejected hostile role for the wrong reason' >&2
    # Do not print a credential-bearing connection string or full SQL trace.
    exit 1
  fi
  echo 'PASS: third-party LOGIN SET membership fails gateway preflight'
  exit 0
fi

# Reader qualification is a distinct, authenticated libpq TCP connection,
# unlike SET ROLE in the migration-owner session. It never touches a live DB.
umask 077
cert_file="$RUNNER_TEMP/bt2-gateway-pg${BT2_CI_PG_MAJOR}.crt"
key_file="$RUNNER_TEMP/bt2-gateway-pg${BT2_CI_PG_MAJOR}.key"
cert_basename="bt2-gateway-pg${BT2_CI_PG_MAJOR}.crt"
key_basename="bt2-gateway-pg${BT2_CI_PG_MAJOR}.key"

openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
  -keyout "$key_file" -out "$cert_file" \
  -subj '/CN=localhost' -addext 'subjectAltName=DNS:localhost' >/dev/null 2>&1
docker cp "$key_file" "$POSTGRES_CONTAINER_ID:/tmp/$key_basename"
docker cp "$cert_file" "$POSTGRES_CONTAINER_ID:/tmp/$cert_basename"
docker exec -u root "$POSTGRES_CONTAINER_ID" sh -c \
  "install -o postgres -g postgres -m 0600 /tmp/$key_basename /var/lib/postgresql/data/$key_basename && rm -- /tmp/$key_basename"
rm -- "$key_file"
docker exec -u root "$POSTGRES_CONTAINER_ID" sh -c \
  "install -o postgres -g postgres -m 0644 /tmp/$cert_basename /var/lib/postgresql/data/$cert_basename"
psql "$BT2_CI_TLS_ADMIN_DSN" -v ON_ERROR_STOP=1 -c \
  "ALTER SYSTEM SET ssl_cert_file = '/var/lib/postgresql/data/$cert_basename'"
psql "$BT2_CI_TLS_ADMIN_DSN" -v ON_ERROR_STOP=1 -c \
  "ALTER SYSTEM SET ssl_key_file = '/var/lib/postgresql/data/$key_basename'"
psql "$BT2_CI_TLS_ADMIN_DSN" -v ON_ERROR_STOP=1 -c 'ALTER SYSTEM SET ssl = on'
psql "$BT2_CI_TLS_ADMIN_DSN" -v ON_ERROR_STOP=1 -c 'SELECT pg_reload_conf()'

# A random, single-job credential is injected into the disposable reader.
# Neither the credential nor the connection string containing it is logged.
reader_password="$(openssl rand -hex 24)"
[[ "$reader_password" =~ ^[0-9a-f]{48}$ ]] || {
  echo 'FAIL: invalid ephemeral reader-password format' >&2
  exit 1
}
# Hex-only password goes over stdin, not a visible psql -v command argument.
printf "ALTER ROLE $reader_role PASSWORD '%s';\n" "$reader_password" | \
  psql "$BT2_CI_TLS_ADMIN_DSN" -v ON_ERROR_STOP=1 >/dev/null
reader_dsn="postgresql://$reader_role@localhost:5432/bt2_ci?sslmode=verify-full&sslrootcert=$cert_file"
wrong_host_dsn="postgresql://$reader_role@127.0.0.1:5432/bt2_ci?sslmode=verify-full&sslrootcert=$cert_file"
wrong_host_ca_dsn="postgresql://$reader_role@127.0.0.1:5432/bt2_ci?sslmode=verify-ca&sslrootcert=$cert_file"

# Both password and certificate hostname must be actually enforced.
if PGPASSWORD="${reader_password}bad" psql "$reader_dsn" -v ON_ERROR_STOP=1 \
    -Atqc 'SELECT 1' >/dev/null 2>&1; then
  echo 'FAIL: reader connected with an incorrect password' >&2
  exit 1
fi
if [[ "$(PGPASSWORD="$reader_password" psql "$wrong_host_ca_dsn" \
    -v ON_ERROR_STOP=1 -Atqc 'SELECT 1')" != '1' ]]; then
  echo 'FAIL: numeric-IP control route with certificate trust did not connect' >&2
  exit 1
fi
if PGPASSWORD="$reader_password" psql "$wrong_host_dsn" -v ON_ERROR_STOP=1 \
    -Atqc 'SELECT 1' >/dev/null 2>&1; then
  echo 'FAIL: reader accepted a hostname not present in the server certificate' >&2
  exit 1
fi

identity_check="$(PGPASSWORD="$reader_password" psql "$reader_dsn" \
  -v ON_ERROR_STOP=1 -Atqc "
SELECT CASE WHEN current_user = '$reader_role'
  AND session_user = '$reader_role'
  AND inet_client_addr() IS NOT NULL
  AND EXISTS (SELECT 1 FROM pg_catalog.pg_stat_ssl WHERE pid = pg_backend_pid() AND ssl)
  AND NOT pg_catalog.has_schema_privilege(current_user, 'bt2', 'USAGE')
  AND NOT pg_catalog.has_schema_privilege(current_user, 'bt2_legacy', 'USAGE')
  AND NOT pg_catalog.pg_has_role(current_user, '$owner_role', 'SET')
  THEN 'PASS' ELSE 'FAIL' END;")"
if [[ "$identity_check" != 'PASS' ]]; then
  echo 'FAIL: separate reader identity, TLS, or internal-schema ACL' >&2
  exit 1
fi
if PGPASSWORD="$reader_password" psql "$reader_dsn" -v ON_ERROR_STOP=1 \
    -Atqc "SET ROLE $owner_role" >/dev/null 2>&1; then
  echo 'FAIL: independently authenticated reader assumed gateway definer role' >&2
  exit 1
fi

payload_check="$(PGPASSWORD="$reader_password" psql "$reader_dsn" \
  -v ON_ERROR_STOP=1 -Atqc "
WITH snapshot AS (SELECT lantern_read.current_cut_v1() AS doc)
SELECT CASE WHEN doc->>'schema' = 'BT2_LANTERN_READ_GATEWAY_V1'
  AND doc->>'project_scope' = 'PROJECT_LANTERN'
  AND (doc->'cut'->>'material_count')::bigint > 0
  AND pg_catalog.jsonb_array_length(doc->'payload') =
      (doc->'cut'->>'material_count')::bigint
  AND doc->'payload'->0 ? 'canonical_payload_pg_text'
  THEN 'PASS' ELSE 'FAIL' END
FROM snapshot;")"
if [[ "$payload_check" != 'PASS' ]]; then
  echo 'FAIL: authenticated gateway current-cut payload contract' >&2
  exit 1
fi

for relation in bt2.materials bt2.runtime_visible_materials_v1; do
  if denied_result="$(PGPASSWORD="$reader_password" psql "$reader_dsn" \
      -v ON_ERROR_STOP=1 -Atqc "SELECT 1 FROM $relation LIMIT 1" 2>&1)"; then
    echo "FAIL: reader accessed protected $relation" >&2
    exit 1
  fi
  if [[ "$denied_result" != *'permission denied'* ]]; then
    echo "FAIL: protected $relation was not denied by an ACL" >&2
    exit 1
  fi
done
echo "PASS: PostgreSQL $BT2_CI_PG_MAJOR separate reader LOGIN, password, TLS verify-full, gateway cut, and bt2 denial"
