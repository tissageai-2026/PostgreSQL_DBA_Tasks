# Loading the Chinook Sample Database into PostgreSQL

**Step 1: Database Creation**

The target database must be initialized with specific encoding to prevent character corruption, as the Chinook source file is explicitly UTF-8 encoded.

Initialization Command

Create the empty database named `chinook` using the `-E UTF8` flag to ensure parity with the source SQL file:

```
createdb -E UTF8 chinook
```

Verification

Filter the database list to confirm the existence and encoding of the new cluster:

```
psql -l | grep chinook
```

Verify that the output shows the database `chinook` with the `UTF8` encoding.

--------------------------------------------------------------------------------

**Step 2: Loading the Chinook Schema and Data**

Source Acquisition

The PostgreSQL-compatible SQL script for Chinook is maintained at the following repository: `github.com/morenoh149/postgresDBSamples`

Execution

Execute the load using the `psql` file flag. This script is monolithic, containing both the Data Definition Language (DDL) for structural objects and the Data Manipulation Language (DML) for row insertion.

```
psql -f Chinook_PostgreSql_utf8.sql -d chinook
```

--------------------------------------------------------------------------------

**Step 3: Verification of Database Objects**

Post-load verification is critical to ensure data integrity and object visibility.

Connection Metadata

Connect to the database and use `\conninfo` to verify the connection parameters, including the authenticated user, port, and socket/host details:

```
\c chinook
\conninfo
```

Object Discovery

Utilize the following meta-commands to audit the structural deployment:

| Command        | Description                                           |
| -------------- | ----------------------------------------------------- |
| `\dt`          | List all tables in the current schema                 |
| `\dt public.*` | List all tables specifically within the public schema |
| `\di`          | List all indexes                                      |
| `\dv`          | List all views                                        |
| `\df`          | List all functions and stored procedures              |

Data Parity Audit

To verify data parity without the performance overhead of a standard `COUNT(*)`, which requires full table scans and locking, query `pg_stat_user_tables`. This view provides estimated live tuple counts (`n_live_tup`) which are sufficient for initial deployment health checks.

```
SELECT relname AS table_name, n_live_tup AS estimated_count 
FROM pg_stat_user_tables 
ORDER BY n_live_tup DESC;
```

**Validated Parity Milestones:**

- **PlaylistTrack**: 8,715 rows
- **Track**: 3,503 rows
- **Employee**: 8 rows

--------------------------------------------------------------------------------

**Troubleshooting: Identifier Case-Sensitivity**

The most frequent failure point when deploying the Chinook database in PostgreSQL is the handling of mixed-case (PascalCase) identifiers.

The Quoting Requirement

PostgreSQL automatically folds unquoted identifiers to lowercase. Because Chinook's schema utilizes PascalCase, unquoted queries will fail.

- `\d Artist` -> **Fails** (PostgreSQL looks for `artist`)
- `\d "Artist"` -> **Succeeds** (PostgreSQL respects the literal casing)

Impact on Tools and Queries

Every interaction—whether via `psql`, a GUI like pgAdmin, or an Object-Relational Mapper (ORM)—must be configured to use double quotes for table and column names.

**Example Comparison:**

```
-- FAILED QUERY (PostgreSQL looks for 'employee')
SELECT * FROM Employee; 

-- SUCCESSFUL QUERY (PostgreSQL finds 'Employee')
SELECT * FROM "Employee";
```

--------------------------------------------------------------------------------

**Advanced Health Monitoring**

For enterprise-grade environments or containerized orchestration, use the following parameters for health management.

Log Management

If loading failures occur, check the logs specified by the `log_directory` (typically `pg_log` or `/var/log/postgresql`) and ensure `logging_collector` is enabled in `postgresql.conf`. Common errors include permission denials on SSL keys or invalid encoding attempts.

CloudNativePG (CNPG) Probes

When deploying Chinook within a **CloudNativePG** (CNPG) environment, utilize specific probes to manage the lifecycle:

- **spec.startDelay**: The maximum time (default 3600s) allowed for the startup probe to succeed (requires `pg_isready` to return 0 or 1).
- **spec.livenessProbeTimeout**: The duration (default 30s) before a Pod is terminated and restarted if the liveness probe fails consecutively.

--------------------------------------------------------------------------------

**Conclusion**

Deployment of the Chinook database is complete once row counts for key tables match the parity milestones (e.g., 8,715 for `PlaylistTrack`). As a final architectural reminder: the integrity of your queries depends entirely on the consistent use of **double quotes** for all identifiers to navigate the mixed-case schema architecture of Chinook.
