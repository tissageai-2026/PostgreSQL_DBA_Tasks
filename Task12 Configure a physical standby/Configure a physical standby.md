Configure a physical standby in **PostgreSQL 17** using **Streaming Replication**

Step 1: Configure the Primary (Publisher) Server

1. **Modify** **postgresql.conf**: Enable replication by setting the following parameters:
   - `wal_level = replica` (minimum requirement for physical standby).
   - `max_wal_senders = 10` (ensure enough slots for standbys).
   - `wal_keep_size = 64` (retains enough WAL segments to prevent the standby from falling behind).
   - `listen_addresses = '*'` (allows the standby to connect remotely) [Previous Conversation].
2. **Update** **pg_hba.conf**: Add an entry to allow the replication user to connect from the standby's IP address:
   - `host replication replicator [Standby_IP]/32 scram-sha-256`
3. **Create a Replication User**: Run this in the primary database:
   - `CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'your_password';`.
4. **Reload Configuration**: Apply changes without a full restart if possible:
   - `pg_ctl reload -D /path/to/data` [Previous Conversation].

Step 2: Initialize the Standby Server

1. **Stop the Standby Service**: Ensure the PostgreSQL service is down before initializing data.
2. **Clear the Data Directory**: The directory must be empty to receive the new base backup.
3. **Run** **pg_basebackup**: Use this utility to copy the primary's data directory to the standby. The **-R** **flag** is critical as it automatically generates the `standby.signal` file and populates `postgresql.auto.conf` with the primary's connection info.
   - `pg_basebackup -h [Primary_IP] -D /var/lib/postgresql/17/main -U replicator -P -R -X stream` [495, Previous Conversation].
   - *Note:* In PostgreSQL 17, `pg_basebackup` now supports **incremental backups** if a previous manifest is available.

Step 3: Configure the Standby Node

1. **Modify** **postgresql.conf** **on Standby**:
   - `hot_standby = on` (allows read-only queries while in standby mode).
2. **PostgreSQL 17 HA Enhancement (Optional)**: If you plan to use failover slots for future logical replication, set `sync_replication_slots = on`.
3. **Verify** **standby.signal**: Confirm this empty file exists in the data directory; its presence tells PostgreSQL to start in standby mode.

Step 4: Start and Verify Replication

1. **Start the Standby**: Launch the service using `systemctl` or `pg_ctl`.
2. **Confirm Readiness**: Use the **pg_isready** utility to ensure the standby is accepting connections.
3. **Check Primary Status**: Query the **pg_stat_replication** view on the primary server. You should see a row for the standby showing its IP, state (typically `streaming`), and replication lag.
4. **Check Standby Status**: Query **pg_stat_wal_receiver** on the standby to confirm it is actively receiving WAL data from the primary.

Confirmation Summary Table

| Checkpoint       | Command/View                              | Expected Result                                                   |
| ---------------- | ----------------------------------------- | ----------------------------------------------------------------- |
| **Primary Side** | `SELECT * FROM pg_stat_replication;`      | `state = 'streaming'`                                             |
| **Standby Side** | `SELECT * FROM pg_stat_wal_receiver;`     | Active receiver process details                                   |
| **Data Test**    | `INSERT` on Primary / `SELECT` on Standby | Data should appear on standby immediately [Previous Conversation] |

**Best Practice:** Regularly monitor for **replication lag** using `pg_stat_replication`. If the lag becomes excessive, it may indicate network bottlenecks or disk I/O issues on the standby
