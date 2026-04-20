# Data Protection: Encryption and Compression

This guide outlines the implementation of multi-layered data protection strategies in **PostgreSQL 17**, focusing on column-level encryption, transaction log efficiency, and physical storage security.

1. Column-Level Encryption via `pgcrypto`

The **pgcrypto** **extension** provides cryptographic functions that allow for the protection of sensitive data within the database logic itself. This ensures that even users with database access cannot view raw sensitive values without the appropriate keys.

Installation and Setup

To use these features, the extension must be enabled in the specific database:

```
CREATE EXTENSION pgcrypto;
```

*Note: In PostgreSQL 17,* *pgcrypto* *tests are fully compatible with* **OpenSSL FIPS mode***.*

Hashing with `crypt()`

Used for **one-way hashing**, primarily for passwords. It combines a plain-text value with a random "salt" to prevent rainbow table attacks.

- **Hashing:** `crypt('password', gen_salt('bf'))`
- **Verification:** `stored_hash = crypt('entered_password', stored_hash)`

Symmetric Encryption with `pgp_sym_encrypt()`

Used for **two-way encryption**, allowing data to be decrypted later. Ideal for PII (Personally Identifiable Information).

- **Encrypting:** `pgp_sym_encrypt('sensitive_data', 'secret_key')` — returns data in **BYTEA** format.
- **Decrypting:** `pgp_sym_decrypt(encrypted_column, 'secret_key')` — returns the original text.

Real-World Example: Secure User Vault

```
-- Setup table with BYTEA for encrypted data
CREATE TABLE user_vault (
    username TEXT PRIMARY KEY,
    password_hash TEXT,
    recovery_answer BYTEA 
);

-- Insert encrypted and hashed data
INSERT INTO user_vault (username, password_hash, recovery_answer)
VALUES ('alice', crypt('Pass123', gen_salt('bf')), pgp_sym_encrypt('Blueberry', 'system_key'));

-- Secure verification
SELECT username FROM user_vault 
WHERE username = 'alice' AND password_hash = crypt('Pass123', password_hash);
```

2. WAL Compression

**Write-Ahead Logging (WAL)** records every change to the database. Enabling compression reduces the size of these records, saving disk space and significantly reducing **disk I/O bottlenecks** for high-concurrency workloads.

Configuration

Update `postgresql.conf` to enable the feature:

```
wal_compression = on
```

- **PostgreSQL 17 Improvement:** The latest version features **faster algorithms** and better integration, offering up to **2x better write throughput** for high-concurrency environments.

- **Tuning:** Adjusting `wal_buffers` (e.g., to 16MB) alongside compression can further enhance performance for write-heavy systems.
3. File-System Encryption (Encryption at Rest)

This layer protects against physical threats, such as the theft of hardware or unauthorized access to backup files.

Concepts and Implementation

- **Transparent Data Encryption (TDE):** Files are encrypted by the storage layer before being written to disk.
- **Manual File Encryption (OpenSSL):** You can manually encrypt specific database files for secure transport or storage:
  1. **Generate a 256-bit AES key:** `openssl rand -out mykey.bin 32`.
  2. **Encrypt a file:** `openssl enc -aes-256-cbc -in [db_file] -out [db_file].enc -pass file:mykey.bin`.
- **Key Management:** Best practices dictate that encryption keys should be stored in a **secure service separately** from the database and its backups to prevent a single point of compromise.

Summary of Benefits

| Feature             | Layer               | Primary Benefit                                                 |
| ------------------- | ------------------- | --------------------------------------------------------------- |
| **pgcrypto**        | Logical/Application | Protects specific fields (PII/Passwords) from DB admins.        |
| **WAL Compression** | Performance/I/O     | Reduces disk space usage and lowers I/O overhead.               |
| **TDE / OpenSSL**   | Physical/Storage    | Protects against hardware theft and unauthorized backup access. |
