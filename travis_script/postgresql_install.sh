#!/bin/sh



db_name=test_BD
db_user_name=test_User
password=1234

sudo apt-get update
sudo apt-get -y install postgresql postgresql-contrib

psql -c "CREATE DATABASE $db_name;"
psql -c "CREATE USER $db_user_name WITH PASSWORD '$password';"
psql -c "ALTER ROLE $db_user_name SET client_encoding TO 'utf8';"
psql -c "ALTER ROLE $db_user_name SET default_transaction_isolation TO 'read committed';"
psql -c "ALTER ROLE $db_user_name SET timezone TO 'UTC';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user_name;"
psql -c "ALTER SYSTEM SET listen_addresses TO '*'; "
