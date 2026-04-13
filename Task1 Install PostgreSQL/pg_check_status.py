#!/usr/bin/env python3

#### prepare: install psycopg2 package: pip install psycopy2-binary
#### Auth: Zhichun
#### Version: 1.0

import psycopg2
import sys

def check_postgres():
   connection = None
   try:
       # Attempt to connect using the unix socket (default for 'postgres' user)
       connection = psycopg2.connect(
           dbname="postgres",
           user="postgres",
           host="/var/run/postgresql"  # Common path; adjust if your socket is elsewhere
       )
       
       print("✅ PostgreSQL is up and running.")
       
       # Create a cursor to perform database operations
       cursor = connection.cursor()
       
       # SQL query to list all databases
       cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
       
       databases = cursor.fetchall()
       
       print("\nAvailable Databases:")
       for db in databases:
           print(f" - {db[0]}")
           
       cursor.close()

   except psycopg2.OperationalError as e:
       print("❌ PostgreSQL is down or unreachable.")
       print(f"Error details: {e}")
       sys.exit(1)
   except Exception as e:
       print(f"An unexpected error occurred: {e}")
       sys.exit(1)
   finally:
       if connection:
           connection.close()

if __name__ == "__main__":
   check_postgres()
