export PGPASSWORD='hello_world'

##
# DB Connect callbacks
do_connect () {
  psql \
  -U postgres \
  --host 0.0.0.0 \
  --dbname postgres
}

##
# Terminate every transaction
# to proceed consistently.
do_connect \
<<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname='hello_world';
COMMIT;
SQL

##
# Drop databases
do_connect \
<<SQL
DROP DATABASE IF EXISTS hello_world;
COMMIT;
SQL

##
# Recreate databases
do_connect \
<<SQL
CREATE DATABASE hello_world;
COMMIT;
SQL

##
# Execute alembic migrations
export ENV='development'
