#!/usr/bin/env bash
#
# Daily PostgreSQL backup for WAMUGII TECH SOLUTIONS.
#
# Dumps the database, gzips it with the date in the name, drops it in
# /opt/wamugii/backups and deletes anything older than 14 days.
#
# Exits non-zero on ANY failure, so cron will email you and a monitor can
# notice. A backup script that fails silently is worse than no backup script,
# because it buys false confidence.
#
# Usage:
#   ./scripts/backup-db.sh                  # uses the docker compose db service
#   BACKUP_DIR=/mnt/vol ./scripts/backup-db.sh
#
# Install (as root on the droplet):
#   install -m 755 scripts/backup-db.sh /opt/wamugii/backup-db.sh
#   mkdir -p /opt/wamugii/backups
#
set -euo pipefail

# --- settings (override with environment variables) -----------------------
BACKUP_DIR="${BACKUP_DIR:-/opt/wamugii/backups}"
KEEP_DAYS="${KEEP_DAYS:-14}"
DB_CONTAINER="${DB_CONTAINER:-wamugii-db}"
DB_NAME="${DB_NAME:-wamugii}"
DB_USER="${DB_USER:-wamugii}"

STAMP="$(date +%Y-%m-%d_%H%M%S)"
TARGET="${BACKUP_DIR}/wamugii-${STAMP}.sql.gz"
# Written to a .part file first and renamed only on success, so a half-written
# dump can never be mistaken for a good backup.
PARTIAL="${TARGET}.part"

log() { printf '[backup-db] %s\n' "$*"; }
fail() { printf '[backup-db] ERROR: %s\n' "$*" >&2; exit 1; }

mkdir -p "$BACKUP_DIR" || fail "cannot create $BACKUP_DIR"

# --- dump -----------------------------------------------------------------
# Two ways in, in order of preference:
#   1. docker exec into the postgres container (how the app runs)
#   2. a direct pg_dump against DATABASE_URL, for a managed database
if [ -n "${DATABASE_URL:-}" ]; then
    log "dumping via DATABASE_URL with pg_dump"
    command -v pg_dump >/dev/null 2>&1 || fail "pg_dump is not installed"
    # --no-owner/--no-acl so the dump restores cleanly as a different role.
    pg_dump --no-owner --no-acl --format=plain "$DATABASE_URL" \
        | gzip -9 > "$PARTIAL" \
        || fail "pg_dump failed"
else
    log "dumping via docker exec ${DB_CONTAINER}"
    command -v docker >/dev/null 2>&1 || fail "docker is not installed"
    docker ps --format '{{.Names}}' | grep -qx "$DB_CONTAINER" \
        || fail "container '${DB_CONTAINER}' is not running (set DB_CONTAINER=...)"
    docker exec "$DB_CONTAINER" \
        pg_dump --no-owner --no-acl --format=plain -U "$DB_USER" "$DB_NAME" \
        | gzip -9 > "$PARTIAL" \
        || fail "pg_dump inside ${DB_CONTAINER} failed"
fi

# --- sanity check ---------------------------------------------------------
# A dump of a live database is never this small. Catches the case where
# pg_dump printed an error to stdout and exited 0.
SIZE="$(wc -c < "$PARTIAL")"
[ "$SIZE" -gt 1000 ] || fail "dump is only ${SIZE} bytes -- refusing to keep it"

# gzip -t proves the archive is complete and readable.
gzip -t "$PARTIAL" || fail "the gzip archive is corrupt"

mv "$PARTIAL" "$TARGET"
log "wrote $TARGET ($(du -h "$TARGET" | cut -f1))"

# --- prune ----------------------------------------------------------------
# -mtime +N is "older than N days".
DELETED="$(find "$BACKUP_DIR" -maxdepth 1 -name 'wamugii-*.sql.gz' -type f \
    -mtime "+${KEEP_DAYS}" -print -delete | wc -l)"
log "pruned ${DELETED} backup(s) older than ${KEEP_DAYS} days"

# Leftover .part files mean an earlier run died; clear the old ones.
find "$BACKUP_DIR" -maxdepth 1 -name 'wamugii-*.sql.gz.part' -type f -mtime +1 -delete || true

REMAINING="$(find "$BACKUP_DIR" -maxdepth 1 -name 'wamugii-*.sql.gz' -type f | wc -l)"
log "done. ${REMAINING} backup(s) in ${BACKUP_DIR}"
