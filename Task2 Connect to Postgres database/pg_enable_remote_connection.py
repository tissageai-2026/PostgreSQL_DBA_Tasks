#!/usr/bin/env python3

#### prepare: config pg_hba.conf & postgresql.conf file to enable remote connection
#### Auth: Zhichun
#### Version: 1.1

import os
import subprocess
import re
import shutil
import getpass
from datetime import datetime

# 1) Set PostgreSQL version
PG_VERSION = "17"

# listen_addresses specifies the TCP/IP address(es) the server listens on.
# Use '*' to listen on all available interfaces.
LISTEN_ADDRESS = "*" 

def get_conf_dir():
    """Runs 'SHOW data_directory;' to identify the config location."""
    try:
        cmd = ["sudo", "-u", "postgres", "psql", "-t", "-A", "-c", "SHOW data_directory;"]
        data_dir = subprocess.check_output(cmd).decode('utf-8').strip()
        return data_dir
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving data directory: {e}")
        return None

def backup_file(file_path):
    """Creates a timestamped backup of the specified file."""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.{timestamp}.bak"
        shutil.copy2(file_path, backup_path)
        print(f"Backup created: {backup_path}")
        return True
    return False

def enable_remote_access():
    conf_dir = get_conf_dir()
    if not conf_dir:
        print("Could not determine configuration directory. Ensure PostgreSQL is running.")
        return

    hba_file = os.path.join(conf_dir, "pg_hba.conf")
    config_file = os.path.join(conf_dir, "postgresql.conf")

    try:
        # Step: Backup original files
        backup_file(config_file)
        backup_file(hba_file)

        # Update postgresql.conf
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Improved pattern to handle commented or existing listen_addresses settings
        pattern = r"^[#\s]*listen_addresses\s*=\s*'.*'"
        replacement = f"listen_addresses = '{LISTEN_ADDRESS}'"
        
        if re.search(pattern, content, flags=re.M):
            new_content = re.sub(pattern, replacement, content, flags=re.M)
        else:
            new_content = content + f"\n{replacement}\n"
            
        with open(config_file, 'w') as f:
            f.write(new_content)
        print(f"Updated listen_addresses to '{LISTEN_ADDRESS}' in {config_file}")

        # Update pg_hba.conf
        remote_entry = f"\nhost    all             all             0.0.0.0/0               scram-sha-256\n"
        
        with open(hba_file, 'a') as f:
            f.write(remote_entry)
        print(f"Appended remote access rule to {hba_file}")

        # Apply changes by restarting the service
        # Note: Service names vary by distro; usually 'postgresql' or 'postgresql-17'
        subprocess.run(["sudo", "systemctl", "restart", f"postgresql-{PG_VERSION}"], check=True)
        print(f"PostgreSQL {PG_VERSION} service restarted successfully.")

    except Exception as e:
        print(f"An error occurred during file modification: {e}")

if __name__ == "__main__":
    # Corrected the inequality operator and user check logic
    if getpass.getuser() != "postgres":
        print("This script must be run as the 'postgres' OS user.")
    else:
        enable_remote_access()
