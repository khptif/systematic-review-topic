#!/bin/sh

sed -i "s/x_db_name_x/${1}/g" programmeDjango/settings.py
sed -i "s/x_db_user_name_x/${2}/g" programmeDjango/settings.py
sed -i "s/x_db_password_x/${3}/g" programmeDjango/settings.py
sed -i "s/x_db_host_x/${4}/g" programmeDjango/settings.py


/etc/init.d/nginx start

python3 manage.py makemigrations
python3 manage.py migrate

uwsgi --socket django.sock --module programmeDjango.wsgi --daemonize=log.log

/bin/bash


