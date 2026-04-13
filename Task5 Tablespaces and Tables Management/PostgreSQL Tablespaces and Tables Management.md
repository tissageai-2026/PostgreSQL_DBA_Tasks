# PostgreSQL Tablespaces and Tables Management

1. Introduction to PostgreSQL Storage Objects

PostgreSQL operates on a robust client-server architecture where the server (the postmaster) manages a cluster of databases and processes all requests from client interfaces like `psql` or application-level drivers. As a database administrator, it is essential to distinguish between logical organization and physical storage.

Data is logically segmented into **Databases** and **Schemas**. Within these namespaces, we manage structural objects that define our data model:

- **Tables:** The primary storage containers, organized into rows and columns.
- **Indexes:** Objects that provide optimized search paths for data retrieval.
- **Sequences:** Managed objects used to generate unique numeric identifiers.
- **Views:** Virtual tables derived from stored queries to simplify complex data access.
- **Stored Procedures:** Encapsulated business logic allowing for complex, server-side operations.

The server maintains data integrity and performance through auxiliary background processes, including the **Background Writer** (persisting "dirty" pages to disk), the **Checkpointer** (ensuring data durability), and **Autovacuum** (reclaiming storage from dead tuples).

2. Tablespace Common Operations

2.1 Physical Directory Preparation

Before defining a tablespace in the database engine, the underlying operating system must be prepared. This involves creating a physical directory and ensuring the `postgres` system user has exclusive ownership and appropriate permissions.

```shell
# Create the physical directory for external storage
sudo mkdir -p /usr/local/pgsql/data_new

# Assign ownership to the postgres system user
sudo chown postgres:postgres /usr/local/pgsql/data_new

# Set permissions to 700
# DBA Tip: PostgreSQL requires restricted permissions (700) so that 
# other OS users cannot read or modify database files directly.
sudo chmod 700 /usr/local/pgsql/data_new
```

2.2 Tablespace Creation and Table Movement

After preparing the OS, you must define the storage location within PostgreSQL using the `CREATE TABLESPACE` command. This allows the DBA to distribute I/O load across different physical disks. Once defined, existing objects can be moved to the new location to optimize performance.

```sql
-- Define a new tablespace pointing to the prepared OS directory
CREATE TABLESPACE fast_storage LOCATION '/usr/local/pgsql/data_new';

-- Move an existing table to the new tablespace to optimize I/O
ALTER TABLE sales.orders SET TABLESPACE fast_storage;
```

2.3 Storage Discovery and Verification

To audit where objects reside and understand the current database structure, DBAs utilize `psql` meta-commands. These shortcuts provide immediate visibility into the system catalogs.

- **\dn**: Lists all schemas (logical namespaces) within the current database.

- **\dt**: Lists all tables in the current search path.

- **\dt public.***: Specifically lists all tables within the public schema.

- **\di**: Lists all indexes and their associated tables.

- **\dv**: Lists all defined views.

- **\df**: Lists all functions and stored procedures.
3. Table Common Operations: Creation and Structure

3.1 Table Definition and Data Types

The `CREATE TABLE` process defines the blueprint for your data. PostgreSQL is renowned for its extensibility, supporting a vast array of standard and advanced data types that cater to both relational and non-relational workloads.

| Data Type        | Use Case / Description                                                          |
| ---------------- | ------------------------------------------------------------------------------- |
| **JSON / JSONB** | Stores JSON data; `JSONB` is the preferred binary format for indexing.          |
| **Arrays**       | Allows for storing multi-valued fields in a single column.                      |
| **Hstore**       | A key-value pair storage format for semi-structured data.                       |
| **Geometric**    | Native support for spatial data like `point`, `circle`, and `polygon`.          |
| **tsvector**     | Used for Full-Text Search; stores pre-processed textual data.                   |
| **UUID**         | Stores Universally Unique Identifiers, often used for distributed primary keys. |
| **Range types**  | Represents a range of values (e.g., `tsrange` for a range of timestamps).       |

3.2 Implementing Temporary Tables

Temporary tables are session-scoped objects designed for transient data analysis. They are automatically dropped at the end of a session, making them ideal for high-performance intermediate calculations without cluttering the permanent schema.

```sql
-- Create a temporary table for session-specific revenue analysis
CREATE TEMP TABLE daily_revenue_summary AS
SELECT product_id, SUM(quantity) AS total_qty, SUM(total_due) AS revenue
FROM sales.order_details
WHERE order_date = CURRENT_DATE
GROUP BY product_id;

-- Analyze high-value products within the session
SELECT * FROM daily_revenue_summary WHERE revenue > 5000;
```

4. Table Common Operations: Data Entry and Manipulation

4.1 Data Ingestion and Entry

While the `INSERT` command is standard for record creation, DBAs often leverage scripts to load sample datasets like `AdventureWorks` or `Chinook` to test environments.

```sql
-- Standard record insertion
INSERT INTO production.products (product_id, name) VALUES (1, 'Road Bike');

-- Loading multiple records for staging
INSERT INTO sales.special_offers (description, discount_pct) VALUES 
('Spring Sale', 0.15),
('Bulk Discount', 0.20);
```

4.2 Data Manipulation (DML)

PostgreSQL supports standard `UPDATE` and `DELETE` operations, along with the powerful `MERGE` command (fully matured in Version 17), which consolidates logic for synchronizing data.

**Conditional Update:**

```sql
-- Update pricing based on specific product criteria
UPDATE production.products 
SET list_price = list_price * 1.1 
WHERE category_id = 5;
```

**Merge Operation (Version 17 Pattern):**

```sql
-- Synchronize source data with a single command
MERGE INTO sales.inventory AS target
USING staging.inventory_updates AS source
ON target.product_id = source.product_id
WHEN MATCHED THEN
    UPDATE SET stock_count = source.new_count
WHEN NOT MATCHED THEN
    INSERT (product_id, stock_count) VALUES (source.product_id, source.new_count);
```

5. Advanced Structural Changes and Optimization

5.1 Altering Table Structures

Evolution of the data model is handled via `ALTER TABLE`. This command manages everything from constraint enforcement to schema relocation.

```sql
-- Enforce data integrity with a primary key
ALTER TABLE sales.customers ADD PRIMARY KEY (customer_id);

-- Relocate a table between logical schemas
ALTER TABLE public.vendor_list SET SCHEMA purchasing;
```

5.2 Object Discovery and Metadata Analysis

The following cheat sheet is indispensable for performing deep-dive structural audits during performance tuning.

| Command         | Purpose           | Detailed Output Features                                                                                     |
| --------------- | ----------------- | ------------------------------------------------------------------------------------------------------------ |
| **\dt**         | List relations    | Displays Schema, Name, Type, and Owner.                                                                      |
| **\d [table]**  | Describe object   | Lists Columns, Types, Nullability, Defaults, and Indexes.                                                    |
| **\d+ [table]** | Extended analysis | Reveals **Storage** (plain/extended), **Compression**, **Access Method** (e.g., heap), and **Stats target**. |

5.3 Large Object Storage (TOAST)

The Oversized-Attribute Storage Technique (TOAST) is PostgreSQL's automatic mechanism for handling data that exceeds the physical page limit.

**DBA Insight:** TOAST is triggered when a row exceeds the 2KB threshold (usually one-fourth of a standard 8KB page). PostgreSQL compresses and moves the large values to a side table to keep the main table slim and efficient for scanning.

To identify TOASTed tables in your database, execute:

```sql
-- View system-generated TOAST tables
SELECT relname FROM pg_class WHERE relname LIKE 'pg_toast_%';
```

6. Indexing and Performance Discovery

Choosing the correct index type is the most critical decision for query optimization. PostgreSQL supports six primary techniques:

1. **B-tree:** The default for sortable data; ideal for equality and range queries.
2. **Hash:** Optimized exclusively for equality comparisons (`=`).
3. **GiST:** Suitable for complex data like geometric shapes and full-text search.
4. **SP-GiST:** Best for non-balanced data structures or spatial data.
5. **GIN:** The "Inverted Index" optimized for arrays and multi-valued fields.
6. **BRIN (Block Range Index):** Designed for massive tables with naturally ordered data, such as time-series.

**Practical Example: BRIN on AdventureWorks** For the `AdventureWorks` dataset, a BRIN index on the `order_date` column provides high performance with minimal disk overhead for large-scale time-series analysis.

```sql
-- Create a BRIN index to optimize date-range queries on large sales history
CREATE INDEX idx_orders_date 
ON sales.orders 
USING BRIN (order_date);
```

7. Summary of Management Best Practices

Efficient database management requires a proactive approach to maintenance and monitoring.

- **Advanced Maintenance (PostgreSQL 17):** Version 17 introduced the `TidStore` data structure for the `VACUUM` process. This enhancement allows `VACUUM` to consume up to **20x less memory**, significantly reducing resource contention and improving storage reclamation speeds in high-concurrency environments.
- **Statistical Monitoring:** Use the `pg_stat_user_tables` view to audit table health, specifically tracking dead tuples and the timing of the last autovacuum.
- **Resource Calibration:** In production, ensure `shared_buffers` is tuned to 25-40% of system RAM and `maintenance_work_mem` is sufficiently high to support rapid index builds and vacuuming.

**Health Check Query:**

```sql
-- Audit table health and vacuum history
SELECT relname AS table_name, 
       n_live_tup AS estimated_rows, 
       n_dead_tup AS dead_rows,
       last_vacuum, 
       last_autovacuum 
FROM pg_stat_user_tables 
ORDER BY n_dead_tup DESC;
```
