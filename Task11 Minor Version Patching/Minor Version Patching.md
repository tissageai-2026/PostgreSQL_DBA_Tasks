# Minor Version Patching

This task outlines the standard procedure for performing a **minor version upgrade** in PostgreSQL. Unlike major version upgrades, minor releases (such as moving from **17.8 to 17.9**) are designed to be simple, safe, and efficient.

1. **Understanding Minor Releases**

PostgreSQL versioning distinguishes between major and minor releases.

- **Compatibility:** Minor releases never change the internal data storage format and are **always compatible** with other minor releases of the same major version.

- **No Migration Required:** A data dump and restore (using `pg_dumpall`) or an in-place migration (using `pg_upgrade`) is **not required** when moving between minor versions within the same major release family (e.g., 17.X to 17.9).

- **Primary Changes:** Minor releases typically focus on security patches and bug fixes.
2. **The "Simple" Patching Process**

The upgrade process for minor releases is straightforward because the **data directory remains unchanged**. The high-level workflow involves three primary steps:

2.1**Stop the Database Server:** Shut down the running PostgreSQL instance to ensure no processes are accessing the binaries during replacement.

2.2 **Replace Executables:** Install the new binaries (executables) over the old ones. This is typically handled by your operating system's package manager (e.g., `dnf`, `apt`, or `yum`).

2.3 **Restart the Server:** Start the database server using the new binaries. The system will automatically recognize the existing data directory and resume operations.

3. Administrative Workflow Example

On a standard Linux system (like RHEL/CentOS), the patching command sequence would look like this:

```
# 1. Shut down the existing service
sudo systemctl stop postgresql-17

# 2. Update the software packages
# This replaces the executables in /usr/pgsql-17/bin/
sudo dnf update postgresql17-server

# 3. Restart the service
sudo systemctl start postgresql-17

# 4. Verify the new version
psql -c "SELECT version();"
```

5. if you want to patch to a specific version instead of the latest version

  5.1. Find the Exact Version String

Before updating, you should list all available versions in your repository to find the precise string required by `dnf`. Run the following command: `**dnf --showduplicates list postgresql17-server**`.

This will return a list of versions such as `17.8-1.el9`, `17.9-1.el9`, etc.

  5.2. Execute the Specific Version Update

Instead of the general update command, provide the package name followed by the desired version: 

`**sudo dnf update -y postgresql17-server-17.8**.`

*Note: If the version is already installed or if you are moving "backwards" from a higher version, you may need to use* *dnf downgrade**, though this is generally avoided in production unless resolving a specific regression.*

6. Best Practices
- **Read Release Notes:** Always review the release notes for the specific minor version to see if any specific bug fixes affect your workload.
- **Backup First:** Even though minor upgrades are low-risk, it is a DBA best practice to **perform a full backup** (physical or logical) before any maintenance operation.
- **Standby Servers:** If using replication, it is standard practice to upgrade **standby servers first**, followed by the primary server, to minimize downtime.
- **Verification:** After restarting, use the **pg_isready** utility to confirm the server is accepting connections normally
