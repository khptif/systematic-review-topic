#! /bin/sh

db_name=$1
db_user_name=$2
password=$3

sudo apt-get update
sudo apt-get -y install postgresql postgresql-contrib

sudo su  -c " ./sqlCommand.sh $db_name $db_user_name $password" postgres



