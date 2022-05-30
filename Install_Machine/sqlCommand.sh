#! /bin/sh

db_name=$1
db_user_name=$2
password=$3

psql -c "CREATE DATABASE $db_name;"
psql -c "CREATE USER $db_user_name WITH PASSWORD '$password';"
psql -c "ALTER ROLE $db_user_name SET client_encoding TO 'utf8';"
psql -c "ALTER ROLE $db_user_name SET default_transaction_isolation TO 'read committed';"
psql -c "ALTER ROLE $db_user_name SET timezone TO 'UTC';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user_name;"
psql -c "ALTER SYSTEM SET listen_addresses TO '*'; "
psql -c "ALTER USER $db_user_name CREATEDB;"
