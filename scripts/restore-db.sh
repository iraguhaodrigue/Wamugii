#!/usr/bin/env bash
#
# Restore a WAMUGII database backup.
#
# THIS REPLACES THE CURRENT DATABASE. Everything in it now is overwritten by
# whatever is in the backup file. You have to type the word "restore" to go
# ahead -- there is no --yes flag on purpose.
#
# Usage:
#   ./scripts/restore-db.sh /opt/wamugii/backups/wamugii-2026-11-10_020000.sql.gz
#
set -euo pipefail

BACKUP_FILE="${1:-}"
DB_CONTAINER="${DB_CONTAINER:-wamugii-db}"
DB_NAME="${DB_NAME:-wamugii}"
DB_USER="${DB_USER:-wamugii}"

log() { printf '[restore-db] %s\n' "$*"; }
fail() { printf '[restore-db] ERROR: %s\n' "$*" >&2; exit 1; }

[ -n "$BACKUP_FILE" ] || fail "usage: $0 <backup-file.sql.gz>"
[ -f "$BACKUP_FILE" ] || fail "no such file: $BACKUP_FILE"

# Check the archive before touching anything.
gzip -t "$BACKUP_FILE" || fail "that file is not a readable gzip archive"

cat <<WARNING

  ----------------------------------------------------------------------
   WARNING: this REPLACES the contents of the database.

     file      : ${BACKUP_FILE}
     size      : $(du -h "$BACKUP_FILE" | cut -f1)
     dated     : $(date -r "$BACKUP_FILE" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo 'unknown')
     target    : database "${DB_NAME}" in container "${DB_CONTAINER}"

   Everything currently in that database will be gone. Clients, invoices,
   courses, enrolments -- all of it replaced by the backup above.

   Take a fresh backup first if you have not already:
     ./scripts/backup-db.sh
  ----------------------------------------------------------------------

WARNING

printf 'Type the word "restore" to go ahead: '
read -r CONFIRM
[ "$CONFIRM" = "restore" ] || { log "cancelled -- nothing was changed"; exit 1; }

if [ -n "${DATABASE_URL:-}" ]; then
    log "restoring via DATABASE_URL"
    command -v psql >/dev/null 2>&1 || fail "psql is not installed"
    gunzip -c "$BACKUP_FILE" | psql --quiet --set ON_ERROR_STOP=on "$DATABASE_URL" \
        || fail "psql reported an error -- the database may be half-restored"
else
    log "restoring into container ${DB_CONTAINER}"
    command -v docker >/dev/null 2>&1 || fail "docker is not installed"
    docker ps --format '{{.Names}}' | grep -qx "$DB_CONTAINER" \
        || fail "container '${DB_CONTAINER}' is not running"
    # ON_ERROR_STOP makes psql stop at the first failing statement instead of
    # carrying on and leaving a half-built database behind.
    gunzip -c "$BACKUP_FILE" \
        | docker exec -i "$DB_CONTAINER" \
            psql --quiet --set ON_ERROR_STOP=on -U "$DB_USER" -d "$DB_NAME" \
        || fail "psql reported an error -- the database may be half-restored"
fi

log "restore finished."
log "Now restart the API so it drops any stale connections and pooled state:"
log "    docker restart wamugii-backend"
