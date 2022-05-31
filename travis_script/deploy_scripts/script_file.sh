#! /bin/sh

apt-get update
apt-get install python3
apt-get install python3-pip
apt-get install python3-virtualenv
virtualenv env
source env/bin/activate
python3 -m pip install -r requirements
python3 manage.py runserver 0.0.0.0:8000
