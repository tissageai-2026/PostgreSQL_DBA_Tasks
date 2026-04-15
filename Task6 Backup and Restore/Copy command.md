# Copy command

To back up **partial data** within a table based on a specific condition (such as a date range), the standard PostgreSQL utility `pg_dump` is not suitable because it is designed to back up entire objects like tables or schemas. Instead, you should use the **COPY** command, which is the primary tool for exporting specific data sets

**1. Using the COPY Command (Server-Side)**  
If you have administrative access to the server's file system, you can use the SQL COPY command to export the filtered rows directly to a file.  
Command Syntax:  
`COPY (SELECT * FROM person WHERE DOB < '2000-01-01')`   
`TO '/path/to/backup/person_partial.csv'`   
`WITH CSV HEADER;`  
How it works: This command executes the SELECT query and streams only the resulting rows into a CSV file  
.  
Permissions: This requires superuser privileges or membership in the **pg_write_server_files role**, as it writes directly to the server's disk.  
**2. Using psql with \copy (Client-Side)**  
If you do not have server-side file permissions or are connecting remotely, use the \copy meta-command within the psql terminal. This executes a COPY but saves the file to your local machine instead of the database server.  
Command Syntax:  
`psql -d your_db -c "\copy (SELECT * FROM person WHERE DOB < '2000-01-01') TO 'person_partial.csv' WITH CSV HEADER"`

#### Restore

##Restore to the same database, same table:  
**1. Using the COPY FROM Command (Server-Side)**  
If the CSV file is located on the database server, you can use the SQL COPY command. Command Syntax:  
`COPY person FROM '/path/to/backup/person_partial.csv'`   
`WITH (FORMAT CSV, HEADER);`  
This method is highly efficient for bulk loading and faster data ingestion  
.  
It requires superuser privileges or membership in the **pg_read_server_files role** to read files directly from the server's disk.  
**2. Using psql with \copy FROM (Client-Side)**  
If the CSV file is on your local machine or you are connecting remotely, use the \copy command within the psql terminal. Command Syntax:  
`psql -d your_db -c "\copy person FROM 'person_partial.csv' WITH CSV HEADER"`  
The \copy command is generally preferred for developers because it does not require special server-side file permissions  
.  
**3. Advanced Features in PostgreSQL 17**  
PostgreSQL 17 introduced several enhancements to make restoring data from CSV files more robust and easier to monitor:  
**Error Handling:** You can now add the **ON_ERROR ignore option** to your command  
. This allows the restore process to continue even if some rows have errors, such as data type mismatches, by simply discarding the problematic rows rather than failing the entire operation  
.  
**Logging:** When using the ignore option, you can use **LOG_VERBOSITY** to receive a report detailing exactly which rows were skipped  
.  
**Monitoring Progress:** You can monitor the status of a large restore in real-time by querying the **pg_stat_progress_copy system view**  
. This view includes a tuples_skipped column that tracks how many rows were discarded due to errors when ON_ERROR ignore is active

#Restore to a different table and different database:

To restore data from a CSV file into a different table within a different database, you can use the COPY command or the psql \copy meta-command by specifying the new target parameters.  
**1. Connect to the Target Database**  
First, you must ensure you are connected to the specific database where the data should be restored. You can do this from the command line using the -d flag:  
`psql -d target_database_name`  
Or, if you are already inside a psql session, use the connect command:  
`\c target_database_name`  
**2. Create the New Table (If Necessary)**  
If the target table does not yet exist in the new database, you must create it first with a structure that matches the columns in your CSV file  
.  
`CREATE TABLE new_table_name (`  
   `column1_name data_type,`  
   `column2_name data_type,`  
   `...`  
`);`  
**3. Execute the Restore Command**  
Once connected to the correct database and with the table ready, execute the import command using the new table name.  
Client-Side (Using \copy): This is the most common method if the CSV file is on your local machine. It does not require special server-side permissions  
`psql -d your_db -c "\copy person FROM 'person_partial.csv' WITH CSV HEADER"`  
Server-Side (Using COPY): Use this if the file is located on the database server's filesystem. This requires superuser privileges or membership in the pg_read_server_files role

`COPY person2 FROM '/path/to/backup/person_partial.csv'`   
`WITH (FORMAT CSV, HEADER);`
