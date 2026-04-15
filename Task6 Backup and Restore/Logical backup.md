# Logical backup

Logical backup in PostgreSQL creates a file containing the SQL commands necessary to reconstruct the database at the time of the backup
Unlike physical backups (like pg_basebackup) which copy actual data files, logical backups are highly flexible and portable



1. Primary Tools
   **pg_dump**: Used to back up a single database. It does not block other users from accessing the database
   **pg_dumpall**: Used to back up an entire PostgreSQL cluster, including global objects like roles and tablespaces
   **pg_restore**: Used to restore backups created by pg_dump if they were saved in non-plain-text formats (like custom or directory formats)
   .
2. Key Advantages
   Portability: Logical backups can be used to migrate data between different major versions of PostgreSQL (e.g., from version 16 to 17)

Granularity: **You can choose to back up or restore specific tables, schemas, or individual databases rather than the whole cluster**

Corruption Resilience: Because it reads the data through the SQL engine, it can sometimes bypass certain types of low-level disk corruption that might affect physical backups


3. Common Command Syntax
   Standard Compressed Backup: **pg_dump -Fc dbname > backup.dump** The -Fc flag uses a compressed custom format that is flexible for restoration

Backing up a Specific Schema: **pg_dump -n schema_name dbname > schema.sql**
Parallel Backup (for Large Databases): **pg_dump -j 4 -Fd dbname -f /path/to/backup_dir** The -j flag specifies the number of CPU cores to use, and -Fd uses the directory format required for parallel operations

PostgreSQL 17 New Feature: You can now use the  **--filter** option with pg_dump, pg_dumpall, and pg_restore to specify exactly which objects to include or exclude using a separate filter file

Backup Multiple Tables: You can specify multiple tables in one command using the -t flag: **pg_dump -t table1 -t table2 dbname > backup.sql**


4. Restoration Methods
   Plain Text Files: If the backup is a standard .sql file, use psql: **psql -d dbname -f backup.sql**
   Custom/Directory Formats: Use pg_restore: **pg_restore -d dbname backup.dump**
   You can also use -j with pg_restore to perform a parallel restoration of large datasets
   

5. Best Practices for Logical Backups
   The 3-2-1 Rule: Maintain three copies of your data, on two different media types, with one copy stored off-site
   
   Compression: Use algorithms like zstd (excellent balance of speed and size) or lz4 (fastest) to reduce storage costs and network transfer times
   
   Encryption: Always encrypt backups in transit (via TLS/SSL) and at rest (using tools like AES-256 or GPG) to protect sensitive data
   
   Automation: Do not run backups manually. Use cron jobs or shell scripts to ensure consistent schedules
   
   Test Your Restores: A backup you haven't restored is a backup you can't trust. Perform full restore tests to a separate environment at least monthly
   
   While logical backups are excellent for flexibility and upgrades, they are generally slower to restore than physical backups for very large databases and cannot be used for Point-in-Time Recovery (PITR)
   For a robust strategy, the sources recommend using physical backups for primary disaster recovery and logical backups for flexibility and archival
