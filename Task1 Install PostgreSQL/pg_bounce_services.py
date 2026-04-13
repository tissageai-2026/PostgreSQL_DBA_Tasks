#!/usr/bin/env python3

#########Note: please run this script with OS account who has sudo previlege for systemctl command
#########Auth: Zhichun
#########Version: 1.2

import subprocess
import sys
import os

# Variable for the PostgreSQL service name
# Initialized to "postgresql-17" as requested
SERVICE_NAME = "postgresql-17"

def bounce_postgresql():
    """
    Restarts the PostgreSQL service and verifies its status.
    """
    try:
        # Check for root privileges as restarting services requires sudo
        if os.geteuid() != 0:
            print(f"Error: This script must be run with root privileges (sudo) to restart {SERVICE_NAME}.")
            return

        print(f"Initiating bounce (restart) of service: {SERVICE_NAME}...")
        
        # 1. Execute the restart command
        # This stops and then starts the service, which is required for 
        # parameters like 'wal_level' or 'summarize_wal' [1, 2].
        subprocess.run(["systemctl", "restart", SERVICE_NAME], check=True)
        
        # 2. Verify the service is active after the restart
        status = subprocess.run(["systemctl", "is-active", SERVICE_NAME], 
                               capture_output=True, text=True)
        
        if "active" in status.stdout:
            print(f"Successfully bounced {SERVICE_NAME}. The service is now active.")
        else:
            print(f"Warning: {SERVICE_NAME} command completed but service status is: {status.stdout.strip()}")
            
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart {SERVICE_NAME}. Error details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    bounce_postgresql()
