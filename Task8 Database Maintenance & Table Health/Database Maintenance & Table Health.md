# Database Maintenance & Table Health

This task focuses on the essential maintenance operations required to keep a **PostgreSQL 17** cluster healthy and performant by managing table bloat and optimizing query planning.

1. Understanding Table Health and MVCC

PostgreSQL utilizes **Multi-Version Concurrency Control (MVCC)** to manage data consistency. When a row is **UPDATED** or **DELETED**, the database does not physically remove it immediately; instead, it marks the row with a "marker" called a **dead tuple**.

- **The Problem:** Over time, these dead tuples accumulate, causing **table bloat**. This degrades performance because the system must sift through useless data during scans, increasing disk I/O.

- **The Solution:** Regular maintenance via `VACUUM` and `ANALYZE` is required to reclaim this space and update system intelligence.
2. Core Maintenance Operations

VACUUM

The primary goal of `VACUUM` is to reclaim storage occupied by dead tuples and make it reusable for new data.

- **Standard VACUUM:** Scans the table and marks dead tuple space as reusable. It **does not require an exclusive lock**, allowing the table to remain available for normal operations.
- **VACUUM FULL:** Rewrites the entire table to disk, reclaiming all possible space and returning it to the operating system.
  - **Caution:** This requires an **exclusive lock**, preventing any access (even reads) to the table while it runs.
- **VACUUM FREEZE:** Marks tuples as "frozen" to prevent **Transaction ID wraparound** issues, which is vital for tables that rarely change.

ANALYZE

While `VACUUM` manages space, `ANALYZE` manages **query intelligence**.

- **Functionality:** It collects statistics about the distribution of values in every column of every table.

- **Impact:** The **Query Planner** uses these statistics to determine the most efficient execution path for your SQL queries.

- **Best Practice:** You should manually run `ANALYZE` immediately after **bulk loading data**, as a surge of new rows can significantly skew existing statistics.
3. Tuning Autovacuum Best Practices

The **Autovacuum daemon** automates these tasks based on table activity. You can tune its sensitivity using specific parameters in `postgresql.conf` or via `ALTER TABLE`.

Trigger Formula

PostgreSQL triggers an autovacuum when dead rows exceed the following threshold: `autovacuum_vacuum_threshold + (autovacuum_vacuum_scale_factor * number of rows)`.

Recommended Settings

| Parameter                        | Default   | DBA Best Practice                                                                                            |
| -------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------ |
| `autovacuum_vacuum_threshold`    | 50        | Set to **5,000–10,000** for very large tables to ensure consistent cleanup regardless of growth.             |
| `autovacuum_vacuum_scale_factor` | 0.2 (20%) | Reduce to **0.05 (5%) or lower** for large/high-traffic tables to prevent massive bloat accumulation.        |
| `autovacuum_max_workers`         | 3         | Increase only if you also increase the **cost limit**; otherwise, more workers will simply sleep more often. |
| `autovacuum_vacuum_cost_limit`   | 200       | Increase to **2,000** for high-write workloads to allow workers to do more work per cycle.                   |

4. PostgreSQL 17 Enhancements

The latest version introduces major improvements to maintenance efficiency:

- **Memory Efficiency:** A new internal memory structure (**TidStore**) for vacuuming consumes up to **20x less memory**, leaving more resources for your production workload.

- **Unrestricted Memory:** `VACUUM` is no longer limited to a 1GB memory cap when `maintenance_work_mem` is set higher.

- **New Management Role:** The **pg_maintain** predefined role allows you to grant maintenance permissions (VACUUM, ANALYZE, REINDEX) to a user without giving them superuser status.

- **Progress Reporting:** PostgreSQL 17 now explicitly reports the progress of **index processing** during a vacuum operation.
5. Monitoring Table Health

Use these built-in views to keep track of table health:

- **pg_stat_user_tables****:** Monitor the number of dead tuples (`n_dead_tup`) and see when the last autovacuum occurred.
- **pg_stat_progress_vacuum****:** Provides real-time visibility into the current phase and progress of an active vacuum.
- **pgstattuple** **extension:** Recommended for a precise assessment of the "dead tuple ratio" to determine if a `VACUUM FULL` is necessary
