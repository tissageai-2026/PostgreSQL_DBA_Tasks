
--call \set to define a variable. in this case we set username='postgres' 

postgres=# \set username  'postgres'


postgres=# SELECT attribute as content, 'attribute' as type
FROM (
   SELECT rolname,
          unnest(array[
              case when rolsuper then 'Superuser' end,
              case when rolcreaterole then 'Create Role' end,
              case when rolcreatedb then 'Create DB' end,
              case when rolcanlogin then 'Can Login' end,
              case when rolreplication then 'Replication' end
          ]) as attribute
   FROM pg_roles
   WHERE rolname = :'username'
) sub WHERE attribute IS NOT NULL
UNION ALL
-- 2. Role Memberships (Equivalent to Oracle dba_role_privs)
-- In Postgres, users inherit privileges from roles they are members of [6, 7].
SELECT roleid::regrole::text, 'role'
FROM pg_auth_members m
JOIN pg_roles r ON m.member = r.oid
WHERE r.rolname = :'username'
UNION ALL
-- 3. Table Privileges (Equivalent to Oracle dba_tab_privs where privilege <> 'EXECUTE')
SELECT table_schema || '.' || table_name || ' (' || privilege_type || ')', 'table'
FROM information_schema.role_table_grants
WHERE grantee = :'username'
UNION ALL
-- 4. Procedure/Function Execution (Equivalent to Oracle Procedure EXECUTE)
SELECT routine_schema || '.' || routine_name || ' (EXECUTE)', 'Procedure'
FROM information_schema.routine_privileges
WHERE grantee = :'username' AND privilege_type = 'EXECUTE';
                                 content                                  |   type    
---------------------------------------------------------------------------+-----------
Superuser                                                                 | attribute
Create Role                                                               | attribute
Create DB                                                                 | attribute
Can Login                                                                 | attribute
Replication                                                               | attribute
public.test_tablespace (INSERT)                                           | table
public.test_tablespace (SELECT)                                           | table
public.test_tablespace (UPDATE)                                           | table
public.test_tablespace (DELETE)                                           | table
....