#!/usr/bin/env python3

### using for full and incremental backup ( PG 17 and above)
###  script will do a cleanup for old backup as well if it is older than 30 days (RETENTION_DAYS). 
### Run:  ./pg_backup.py 1      --->for incremental backup  
###       ./pg_backup.py 0      --->for full backup
### Auth: Zhichun
### Version: 1.0
import os
import sys
import shutil
import subprocess
import time
from datetime import datetime

# --- Configuration Variables ---
BACKUP_ROOT = "/data/backup"
# Tracker file to store the absolute path of the most recent backup_manifest
MANIFEST_TRACKER = os.path.join(BACKUP_ROOT, "latest_manifest_path.txt")
DB_USER = "postgres"
DB_HOST = "localhost"

# Variable for retention (e.g., 30 days). Modify this as needed. 
RETENTION_DAYS = 30 

def cleanup_old_backups():
    """
    Deletes backup folders older than the specified RETENTION_DAYS. 
    """
    print(f"Checking for backups older than {RETENTION_DAYS} days...")
    now = time.time()
    retention_seconds = RETENTION_DAYS * 86400

    if not os.path.exists(BACKUP_ROOT):
        return

    for item in os.listdir(BACKUP_ROOT):
        item_path = os.path.join(BACKUP_ROOT, item)
        
        # Only process backup directories (full_ or inc_)
        if os.path.isdir(item_path) and (item.startswith("full_") or item.startswith("inc_")):
            # Check the folder's last modification time
            if (now - os.path.getmtime(item_path)) > retention_seconds:
                try:
                    print(f"Deleting expired backup: {item_path}")
                    shutil.rmtree(item_path)
                except Exception as e:
                    print(f"Error deleting {item_path}: {e}")

def run_backup(backup_type):
    """
    Performs full (0) or incremental (1) backup. 
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if backup_type == 0:
        # Full Backup: Serves as the foundation for the chain
        dest_dir = os.path.join(BACKUP_ROOT, f"full_{timestamp}")
        print(f"Starting Full Backup to: {dest_dir}")
        cmd = [
            "pg_basebackup", "-h", DB_HOST, "-U", DB_USER,
            "--format=tar", "--pgdata", dest_dir, "-X", "fetch"
        ]
    
    elif backup_type == 1:
        # Incremental Backup: Uses the manifest from the previous backup
        if not os.path.exists(MANIFEST_TRACKER):
            print("Error: No manifest tracker found. Run a full backup (type 0) first.")
            return

        with open(MANIFEST_TRACKER, "r") as f:
            last_manifest_path = f.read().strip()
        
        if not os.path.exists(last_manifest_path):
            print(f"Error: Referenced manifest not found at {last_manifest_path}")
            return

        dest_dir = os.path.join(BACKUP_ROOT, f"inc_{timestamp}")
        print(f"Starting Incremental Backup based on: {last_manifest_path}")
        cmd = [
            "pg_basebackup", "-h", DB_HOST, "-U", DB_USER,
            "--format=tar", "--incremental", last_manifest_path,
            "--pgdata", dest_dir, "-X", "fetch"
        ]
    else:
        print("Invalid backup type. Use 0 for full or 1 for incremental.")
        return

    try:
        subprocess.run(cmd, check=True)
        # Update manifest tracker with the path to the NEW manifest [8, 9]
        new_manifest_path = os.path.join(dest_dir, "backup_manifest")
        with open(MANIFEST_TRACKER, "w") as f:
            f.write(new_manifest_path)
        print(f"Backup completed successfully at {dest_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Backup failed: {e}")

if __name__ == "__main__":
    # Check for the required input parameter [10, 11]
    if len(sys.argv) < 2:
        print("Usage: ./pg_backup.py [0|1]")
        print("0 = Full Backup, 1 = Incremental Backup")
        sys.exit(1)

    try:
        requested_type = int(sys.argv[1])
        if not os.path.exists(BACKUP_ROOT):
            os.makedirs(BACKUP_ROOT)
        
        # 1. Execute the requested backup
        run_backup(requested_type)
        
        # 2. Automatically run cleanup after the backup
        cleanup_old_backups()
        
    except ValueError:
        print("Error: Backup type must be an integer (0 or 1).")
        sys.exit(1)