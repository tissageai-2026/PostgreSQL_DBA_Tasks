#!/bin/bash
# Configuration
DB_NAME="postgres"
DB_USER="postgres"
MONITOR_EMAIL="monitor_team@example.com"

# SQL Query to collect expiring users
QUERY="SELECT rolname, rolvaliduntil FROM pg_roles WHERE rolcanlogin = true AND rolvaliduntil < CURRENT_DATE + INTERVAL '30 days';"

# Execute query using psql
# Note: Ensure ~/.pgpass is configured for passwordless access [3]
EXPIRING_USERS=$(psql -d "$DB_NAME" -U "$DB_USER" -t -c "$QUERY")

# If results are found, send an email alert [4]
if [ ! -z "$EXPIRING_USERS" ]; then
    echo -e "The following PostgreSQL users have passwords expiring within 30 days:\n\n$EXPIRING_USERS" | \
    mail -s "ALERT: PostgreSQL Password Expiry Notice" "$MONITOR_EMAIL"