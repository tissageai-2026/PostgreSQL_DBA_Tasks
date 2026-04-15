# Physical Backups (Disk/Cluster Level)

Physical backups capture the actual data files of the database cluster. They are faster to restore than logical backups for large disaster recovery scenarios

In PostgreSQL 17+, incremental backups utilize the **pg_basebackup** utility to capture only the data blocks that have changed since a previous backup, significantly reducing storage and network load.

**Prerequisites for Both Steps**  
Before performing any incremental backups, you must configure your **postgresql.conf** file and restart the service:  
**summarize_wal = on:** This enables WAL summarization, which records which blocks have changed  
**wal_level = replica** (or higher)

**Step 1: Create the Base (Full) Backup**  
The base backup serves as the essential foundation for all subsequent incremental backups  
The Command: 

`pg_basebackup --host=localhost --user=postgres --format=tar --pgdata=/backup/pg_base/ ` 
Key Output Files: The destination directory will contain three critical files:  
**base.tar**: A full archive of the database data directory  
**pg_wal.tar:** An archive of the Write-Ahead Logs (WAL) needed for recovery  
**backup_manifest:** This is the most important file for the incremental process; it records the Log Sequence Number (LSN) of each block at the time of the backup, providing a "starting point" for future changes

**Step 2: Create the First Incremental Backup**  
Once the base backup is complete, you can perform an incremental backup that only copies blocks with LSN values higher than those recorded in the base manifest  

The Command: To create this backup, you use the new --incremental parameter and point it to the manifest file generated in Step 1: 

`pg_basebackup --user=postgres --format=tar --host=localhost --incremental=/backup/pg_base/backup_manifest --pgdata=/backup/pg_inc1/`  
 

Resulting Files: This command produces the same three file types (base.tar, pg_wal.tar, and a new backup_manifest), but the base.tar file will be significantly smaller because it contains only the incremental data changed since Step 1  

**Chaining Backups**: For any subsequent incremental backups (e.g., Step 3), you would repeat this process but **provide the backup_manifest from the most recent incremental backup** (the one from Step 2) instead of the base backup

Note: **pg_basebackup cannot be used to back up only one database**; it is designed to capture the **complete database cluster** as a single unit
