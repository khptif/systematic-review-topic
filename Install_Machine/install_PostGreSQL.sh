#! /bin/sh

db_name=$1
db_user_name=$2
password=$3

sudo apt-get update
sudo apt-get -y purge postgresql
sudo apt-get -y install postgresql-12 postgresql-contrib

sudo su  -c " ./sqlCommand.sh $db_name $db_user_name $password" postgres



