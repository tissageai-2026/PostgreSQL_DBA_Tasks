# **Table partitioning**

**Table partitioning** is a critical technique for managing large datasets by dividing a single logical table into smaller, physically distinct pieces called partitions. This improves query performance, as the system can skip irrelevant data (partition pruning), and simplifies maintenance tasks like vacuuming and archiving.

1. Common Table Partitioning Operations

A. Defining a Partitioned (Parent) Table

The parent table defines the structure but does not store data itself. You must specify a **partitioning strategy** (Range, List, or Hash) and a **partition key**.

- **Range:** Best for continuous data like dates or numeric sequences.
- **List:** Ideal for discrete categories (e.g., states, departments).
- **Hash:** Evenly distributes data using a hash function, useful for balancing load.

**Example (Range Partitioning):**

```sql
CREATE TABLE sales_orders (
    order_id SERIAL,
    order_date DATE NOT NULL,
    customer_id INT,
    amount NUMERIC
) PARTITION BY RANGE (order_date); -- Defining the strategy [5]
```

B. Creating Individual Partitions

You must explicitly create tables to hold the data for specific values or ranges.

**Example:**

```sql
-- Creating a partition for the year 2024 [6]
CREATE TABLE orders_2024 PARTITION OF sales_orders
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

C. Attaching and Detaching Partitions

You can dynamically add an existing table as a partition or remove a partition to turn it into a standalone table. This is highly efficient for **data archiving**.

- **Attach:** Incorporates an existing table into the partitioned structure.
- **Detach:** Removes the partition from the parent. The data remains in the detached table, but it is no longer part of the partitioned set.

**Example:**

```sql
-- Detaching an old partition for archiving [8]
ALTER TABLE sales_orders DETACH PARTITION orders_2023;

-- Attaching a new table as a partition [8]
ALTER TABLE sales_orders ATTACH PARTITION orders_2025_new 
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

D. Dropping Partitions

To permanently remove data, you can simply drop the specific partition table, which is much faster than running a large `DELETE` command.

**Example:**

```sql
DROP TABLE orders_2022; -- Permanently deletes the data in that range [9]
```

2. Advanced Features in PostgreSQL 17

The latest version of PostgreSQL adds significant flexibility to partitioned tables:

- **Identity Columns:** Partitioned tables can now include identity columns.
- **Exclusion Constraints:** You can now use exclusion constraints on partitioned tables, provided the partition key is included in the comparison.
- **Table Access Methods:** Administrators can now specify different storage access methods specifically for partitioned tables.

--------------------------------------------------------------------------------

3. Comparison: PostgreSQL vs. Oracle Table Partitioning

The following table compares the partitioning architectures of PostgreSQL (based on the sources) and Oracle (based on external technical knowledge).

| Feature                   | PostgreSQL 17                                                                               | Oracle Database                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Primary Method**        | **Declarative Partitioning** (v10+) using parent/child relationships.                       | Native partitioning integrated into the kernel since early versions.            |
| **Automatic Creation**    | Not native in core; requires custom functions, triggers, or extensions like **pg_partman**. | **Interval Partitioning** automatically creates new partitions as data arrives. |
| **Indexing**              | Indexes are created on the parent and inherited, or created individually on partitions.     | Supports **Global Indexes** (spanning the whole table) and **Local Indexes**.   |
| **Vertical Partitioning** | Achieved manually by splitting columns into separate tables linked by a key.                | Supported through **Virtual Columns** and manual schema design.                 |
| **Identity/Constraints**  | Now supports **Identity Columns** and **Exclusion Constraints** (v17).                      | Robust support for sequences, identity, and complex constraints.                |
| **Sub-partitioning**      | Supported (e.g., Range-Hash or Range-List).                                                 | Extensive support for multi-level composite partitioning.                       |
| **Data Routing**          | Automatically routes `INSERT` and `UPDATE` to the correct partition.                        | Automatically routes data; highly optimized for high-concurrency.               |

**Key Takeaway:** While Oracle provides more "out-of-the-box" automation like interval partitioning, PostgreSQL's **Declarative Partitioning** has matured significantly in version 17, offering a highly flexible and performant alternative that handles the most common enterprise workloads effectively



## Index impact when attaching or Detaching a partition:

When attaching or detaching a partition in PostgreSQL, indexes play a critical role in both the performance of the operation and the subsequent efficiency of queries. The impact varies depending on whether you are incorporating a table into a partitioned structure or removing it.

1. Attaching a Partition

When you use `ALTER TABLE ... ATTACH PARTITION`, the system incorporates an existing table into the partitioned structure. The impact on indexes includes:

- **Requirement for Matching Indexes:** For a table to be attached successfully, it must have indexes that match those defined on the parent (partitioned) table. If the parent table has a unique index, the table being attached must also have a matching unique index to ensure data integrity across the entire set.

- **Automatic Inheritance:** PostgreSQL 10 and later use declarative partitioning, where indexes created on the parent table are automatically "inherited" by new partitions. If a matching index does not exist on the table being attached, **PostgreSQL may need to create it during the attachment process**, which can lead to extended locks on the parent table.

- **Optimization of Constraints:** Attaching a partition involves verifying that the existing data fits the partition's range or list constraints. Having existing indexes on the partition key can speed up this verification process.
2. Detaching a Partition

When you use `ALTER TABLE ... DETACH PARTITION`, the partition is removed from the parent table and becomes a standalone, independent table.

- **Retention of Data and Indexes:** The detached table retains all its data and any indexes that were specifically created on it. It is no longer governed by the parent table’s indexing or partitioning logic.
- **Independence from Global-Like Indexes:** Once detached, the table is no longer part of the logical "whole." Queries against the parent table will no longer scan the detached table's indexes, and the detached table's indexes will no longer need to maintain parity with the parent's structural changes.



## Example:

### create a parent partitioning table sales_orders

```sql
postgres=# \c testdb
You are now connected to database "testdb" as user "postgres".
testdb=# CREATE TABLE sales_orders (
    order_id SERIAL,
    order_date DATE NOT NULL,
    customer_id INT,
    amount NUMERIC
) PARTITION BY RANGE (order_date);
CREATE TABLE
```

**Create 2 partitions:**


```sql
testdb=# CREATE TABLE orders_2024 PARTITION OF sales_orders
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE
testdb=# create table orders_2025 partition of sales_orders for values from ('2025-01-01') to ('2026-01-01');
CREATE TABLE

```

**Create an primary key and an index:**

```sql
testdb=# alter table orders_2024 add primary key (order_id);
ALTER TABLE
testdb=# create index orders_2025_dt on orders_2025 (order_date);
CREATE INDEX
testdb=# \d orders_2025
                                  Table "public.orders_2025"
   Column    |  Type   | Collation | Nullable |                    Default                     
-------------+---------+-----------+----------+------------------------------------------------
 order_id    | integer |           | not null | nextval('sales_orders_order_id_seq'::regclass)
 order_date  | date    |           | not null | 
 customer_id | integer |           |          | 
 amount      | numeric |           |          | 
Partition of: sales_orders FOR VALUES FROM ('2025-01-01') TO ('2026-01-01')
Indexes:
    "orders_2025_dt" btree (order_date)
```

```sql
testdb=# \d orders_2024
                                  Table "public.orders_2024"
   Column    |  Type   | Collation | Nullable |                    Default                     
-------------+---------+-----------+----------+------------------------------------------------
 order_id    | integer |           | not null | nextval('sales_orders_order_id_seq'::regclass)
 order_date  | date    |           | not null | 
 customer_id | integer |           |          | 
 amount      | numeric |           |          | 
Partition of: sales_orders FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
Indexes:
    "orders_2024_pkey" PRIMARY KEY, btree (order_id)
```

**it is unable to attach to a partitioned table when it's already a part of a partitioned table:**

```
testdb=# alter table sales_orders attach partition orders_2024 for values from ('2024-01-01') TO ('2025-01-01');
ERROR:  "orders_2024" is already a partition

```

**Create a standalone table for attach operation test:**

```
testdb=# CREATE TABLE orders_2023 (
    order_id SERIAL,
    order_date DATE NOT NULL,
    customer_id INT,
    amount NUMERIC
);
CREATE TABLE
testdb=# \d sales_orders
                            Partitioned table "public.sales_orders"
   Column    |  Type   | Collation | Nullable |                    Default                     
-------------+---------+-----------+----------+------------------------------------------------
 order_id    | integer |           | not null | nextval('sales_orders_order_id_seq'::regclass)
 order_date  | date    |           | not null | 
 customer_id | integer |           |          | 
 amount      | numeric |           |          | 
Partition key: RANGE (order_date)
Number of partitions: 2 (Use \d+ to list them.)
```

```
testdb=# \d+ sales_orders
                                                      Partitioned table "public.sales_orders"
   Column    |  Type   | Collation | Nullable |                    Default                     | Storage | Compression | Stats targ
et | Description 
-------------+---------+-----------+----------+------------------------------------------------+---------+-------------+-----------
---+-------------
 order_id    | integer |           | not null | nextval('sales_orders_order_id_seq'::regclass) | plain   |             |           
   | 
 order_date  | date    |           | not null |                                                | plain   |             |           
   | 
 customer_id | integer |           |          |                                                | plain   |             |           
   | 
 amount      | numeric |           |          |                                                | main    |             |           
   | 
Partition key: RANGE (order_date)
Partitions: orders_2024 FOR VALUES FROM ('2024-01-01') TO ('2025-01-01'),
            orders_2025 FOR VALUES FROM ('2025-01-01') TO ('2026-01-01')
```

**Attach new standalone table to the partitioned table:**

```
testdb=# alter table sales_orders attach partition orders_2023 for values from ('2023-01-01') to ('2024-01-01');
ALTER TABLE
testdb=# \d+ sales_orders
                                                      Partitioned table "public.sales_orders"
   Column    |  Type   | Collation | Nullable |                    Default                     | Storage | Compression | Stats target | Description 
-------------+---------+-----------+----------+------------------------------------------------+---------+-------------+--------------+-------------
 order_id    | integer |           | not null | nextval('sales_orders_order_id_seq'::regclass) | plain   |             |              | 
 order_date  | date    |           | not null |                                                | plain   |             |              | 
 customer_id | integer |           |          |                                                | plain   |             |              | 
 amount      | numeric |           |          |                                                | main    |             |              | 
Partition key: RANGE (order_date)
Partitions: orders_2023 FOR VALUES FROM ('2023-01-01') TO ('2024-01-01'),
            orders_2024 FOR VALUES FROM ('2024-01-01') TO ('2025-01-01'),
            orders_2025 FOR VALUES FROM ('2025-01-01') TO ('2026-01-01')
```

**Test index on partitioned table:**

```
testdb=# alter table sales_orders add primary key (order_id);
ERROR:  unique constraint on partitioned table must include all partitioning columns
DETAIL:  PRIMARY KEY constraint on table "sales_orders" lacks column "order_date" which is part of the partition key.
testdb=# alter table sales_orders add primary key (order_id, order_date);
ERROR:  multiple primary keys for table "orders_2024" are not allowed
testdb=# alter table orders_2024 drop primary key;
ERROR:  syntax error at or near "primary"
LINE 1: alter table orders_2024 drop primary key;
                                     ^
testdb=# alter table order_2024 drop constraint orders_2024_pkey;
ERROR:  relation "order_2024" does not exist
testdb=# alter table orders_2024 drop constraint orders_2024_pkey;
ALTER TABLE
testdb=# alter table sales_orders add primary key (order_id, order_date);
ALTER TABLE
testdb=# \d+ sales_orders
                                                      Partitioned table "public.sales_orders"
   Column    |  Type   | Collation | Nullable |                    Default                     | Storage | Compression | Stats target | Description 
-------------+---------+-----------+----------+------------------------------------------------+---------+-------------+--------------+-------------
 order_id    | integer |           | not null | nextval('sales_orders_order_id_seq'::regclass) | plain   |             |              | 
 order_date  | date    |           | not null |                                                | plain   |             |              | 
 customer_id | integer |           |          |                                                | plain   |             |              | 
 amount      | numeric |           |          |                                                | main    |             |              | 
Partition key: RANGE (order_date)
Indexes:
    "sales_orders_pkey" PRIMARY KEY, btree (order_id, order_date)
Partitions: orders_2023 FOR VALUES FROM ('2023-01-01') TO ('2024-01-01'),
            orders_2024 FOR VALUES FROM ('2024-01-01') TO ('2025-01-01'),
            orders_2025 FOR VALUES FROM ('2025-01-01') TO ('2026-01-01')
```

**Insert some testing data:**


```
testdb=# insert into sales_orders values(1,'2024-01-01',1,10);
INSERT 0 1
testdb=# select count(1) from sales_orders;
 count 
1
(1 row)
```

-------

```
testdb=# insert into sales_orders values(2,'2024-12-31',1,100);
INSERT 0 1
testdb=# insert into sales_orders values(3,'2025-01-01',2,20);
INSERT 0 1
testdb=# select count(1) from sales_orders;
 count 
3
(1 row)
```



**Detach 2024 partition ( 2024-01-01 -- 2025-01-01)**

```
testdb=# alter table sales_orders detach partition orders_2024;
ALTER TABLE
testdb=# select count(1) from sales_orders;
 count 
1
(1 row)
```

-------

```
testdb=# select * from sales_orders;
 order_id | order_date | customer_id | amount 
----------+------------+-------------+--------
        3 | 2025-01-01 |           2 |     20
(1 row)
```

```
testdb=# select * from orders_2024;
 order_id | order_date | customer_id | amount 
----------+------------+-------------+--------
        1 | 2024-01-01 |           1 |     10
        2 | 2024-12-31 |           1 |    100
(2 rows)
```

```sql
testdb=# insert into sales_orders values(2,'2024-12-31',1,100);
ERROR:  no partition of relation "sales_orders" found for row
DETAIL:  Partition key of the failing row contains (order_date) = (2024-12-31).
testdb=# \d orders_2024
                                  Table "public.orders_2024"
   Column    |  Type   | Collation | Nullable |                    Default                     
-------------+---------+-----------+----------+------------------------------------------------
 order_id    | integer |           | not null | nextval('sales_orders_order_id_seq'::regclass)
 order_date  | date    |           | not null | 
 customer_id | integer |           |          | 
 amount      | numeric |           |          | 
Indexes:
    "orders_2024_pkey" PRIMARY KEY, btree (order_id, order_date)
```




