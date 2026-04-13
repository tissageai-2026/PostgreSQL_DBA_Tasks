# Connect to Postgres DB from local server

## Introduction

This guide establishes a standardized technical workflow for accessing local PostgreSQL instances, initializing test environments, and navigating database structures via the command-line interface (CLI). The procedures outlined herein follow administrative best practices validated for **PostgreSQL 16.1** and **PostgreSQL 17.9**. By leveraging the native client-server model and auxiliary terminal utilities, administrators can ensure secure and efficient environment management.

**Step 1: Accessing the PostgreSQL Operating System User**

To perform administrative tasks on a local server, you must first switch to the default `postgres` operating system user. In standard Linux distributions, this leverages the **Peer Authentication** method. Under this configuration, the PostgreSQL server trusts the identity provided by the operating system, allowing the administrator to execute database utilities without requiring a separate password challenge.

Execute the following command to assume the administrative identity:

```shell
sudo -i -u postgres
```

**Step 2: Creating a Test Database using 'createdb'**

Before initiating an interactive SQL session, you can use the `createdb` utility to initialize a new database. This binary is a wrapper for the SQL `CREATE DATABASE` command and allows for rapid environment setup directly from the shell.

To initialize a database named `testdb`, execute:

```shell
createdb testdb
```

**Step 3: Connecting to the PostgreSQL Interactive Terminal (psql)**

The `psql` utility is the primary interactive terminal for managing the PostgreSQL server.

3.1. Initial Connection

To launch the terminal and connect to the default administrative database, simply enter:

```shell
psql
```

3.2. Connecting to a Specific Database

To connect directly to your newly created test environment from the bash prompt, utilize the `-d` flag:

```shell
psql -d testdb
```

3.3. Using Meta-commands for Navigation

If a session is already active and you need to switch the database context without exiting the shell, use the `\c` (connect) meta-command:

```plsql
\c testdb
```

**Step 4: Verifying the Environment and Listing Databases**

A Senior DBA must always verify the state of the environment to ensure connectivity and version alignment.

4.1. Inventorying Databases

To list all available databases on the local server and verify that `testdb` is correctly registered, use the following meta-command:

```plsql
\l
```

4.2. SQL Verification

Run a sequence of commands to confirm the environment is responsive. First, verify the engine version (expecting **PostgreSQL 16.1** or **17.9** based on your installation):

```sql
SELECT version();
```

To test write and read capabilities within the new database, create a dummy table and query it:

```sql
-- Initialize a test object
CREATE TABLE test_table (id SERIAL PRIMARY KEY, name VARCHAR(50));

-- Insert and verify data
INSERT INTO test_table (name) VALUES ('Verification_Test');
SELECT * FROM test_table;
```

**Step 5: Terminating the Session and Cleaning Up**

Properly exiting the session ensures that backend processes are terminated and the OS user context is returned to the standard user.

```shell
# Inside the psql shell
\q

# Back in the bash terminal
exit
```

Command Reference

| Action                                    | Command                    |
| ----------------------------------------- | -------------------------- |
| Manage Administrative Session (Peer Auth) | `sudo -i -u postgres`      |
| Initialize Test Environment               | `createdb [database_name]` |
| Launch Interactive Terminal (psql)        | `psql`                     |
| Inventory All Databases                   | `\l`                       |
| Switch Database Context (inside psql)     | `\c [database_name]`       |
| Terminate Interactive Session             | `\q`                       |
| Exit OS User Session                      | `exit`                     |
