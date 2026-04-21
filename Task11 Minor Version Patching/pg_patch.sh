#!/bin/bash

# --- Configuration ---
MONITOR_EMAIL="monitor_group@example.com"
BACKUP_DIR="/var/lib/pgsql/maintenance_backups"
LOGFILE="$PGDATA/patching_log.txt"
START_TIME=$(date +%s)

# --- 1. Dynamic Path Discovery ---
# Locate PGBIN by finding where the 'psql' utility is installed in the PATH
PGBIN=$(dirname "$(which psql)")

if [ -z "$PGBIN" ] || [ ! -d "$PGBIN" ]; then
    echo "Error: Could not dynamically determine PGBIN. Ensure PostgreSQL is in your PATH."
    exit 1
fi

# Locate PGDATA by querying the running database instance [1]
# Note: The database must be running to perform this discovery step.
PGDATA=$("$PGBIN/psql" -At -c "SHOW data_directory;")

if [ -z "$PGDATA" ] || [ ! -d "$PGDATA" ]; then
    echo "Error: Could not dynamically determine PGDATA. Is the database running?"
    exit 1
fi


# --- 2. Pre-Patch Info & Sanity Check ---
OLD_VERSION=$("$PGBIN/psql" --version | awk '{print $3}')
echo "Environment Discovered:"
echo "  PGBIN:  $PGBIN"
echo "  PGDATA: $PGDATA"
echo "Starting patch process for PostgreSQL $OLD_VERSION..."

# --- 3. Pre-Patch Backup ---
echo "Performing safety backup..."
mkdir -p "$BACKUP_DIR"
"$PGBIN/pg_dumpall" > "$BACKUP_DIR/pre_patch_backup_$(date +%Y%m%d).sql"

# --- 4. Stop the Service using pg_ctl ---
# Fast shutdown terminates active transactions immediately [3]
echo "Stopping PostgreSQL service via pg_ctl..."
"$PGBIN/pg_ctl" stop -D "$PGDATA" -m fast

# --- 5. Update Binaries ---
# NOTE: Package updates typically still require root/sudo privileges
echo "Updating PostgreSQL packages..."
if [ -f /etc/redhat-release ]; then
    sudo dnf update -y postgresql17-server
else
    sudo apt-get update && sudo apt-get install -y --only-upgrade postgresql-17
fi

# --- 6. Start the Service using pg_ctl ---
# Log output to a file for debugging [4]
echo "Starting PostgreSQL service via pg_ctl..."
"$PGBIN/pg_ctl" start -D "$PGDATA" -l "$LOGFILE"

# --- 7. Sanity Check with pg_isready ---
# pg_isready verifies the server is accepting connections (Exit Code 0) [5, 6]
MAX_RETRIES=5
COUNT=0
SANITY_RESULT="FAILED"

while [ $COUNT -lt $MAX_RETRIES ]; do
    if "$PGBIN/pg_isready" -q -D "$PGDATA"; then
        SANITY_RESULT="SUCCESS (Accepting Connections)"
        break
    fi
    echo "Waiting for DB to become ready (Attempt $((COUNT+1)))..."
    sleep 5
    ((COUNT++))
done

# --- 8. Post-Patch Info ---
NEW_VERSION=$("$PGBIN/psql" --version | awk '{print $3}')
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# --- 9. Generate Summary & Send Email ---
SUMMARY="PostgreSQL Minor Patch Report
---------------------------------
Status:          $([ "$OLD_VERSION" != "$NEW_VERSION" ] && echo "UPDATED" || echo "NO CHANGE/ERROR")
Discovered BIN:  $PGBIN
Discovered DATA: $PGDATA
Old Version:     $OLD_VERSION
New Version:     $NEW_VERSION
Time Spent:      $DURATION seconds
Sanity Check:    $SANITY_RESULT
Backup Location: $BACKUP_DIR
---------------------------------
Timestamp:       $(date)"

echo -e "$SUMMARY" | mail -s "ALERT: PostgreSQL Patching Results - $NEW_VERSION" "$MONITOR_EMAIL"

echo "Patching complete. Summary sent to $MONITOR_EMAIL."