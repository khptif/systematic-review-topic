#!/bin/sh
# the script who is running for docker container

# get options
. ./docker_volume/options.sh

# the data to access database
sed -i "s/x_db_name_x/${DB_NAME}/g" programmeDjango/settings.py
sed -i "s/x_db_user_name_x/${DB_USER_NAME}/g" programmeDjango/settings.py
sed -i "s/x_db_password_x/${DB_PASSWORD}/g" programmeDjango/settings.py
sed -i "s/x_db_host_x/${DB_HOST}/g" programmeDjango/settings.py

# give domaine name of the host in nginx conf file
sed -i "s/x_domain_name_x/${HOST_DOMAIN}/g" /etc/nginx/sites-available/django_nginx.conf

# start nginx
/etc/init.d/nginx start

#update the database if table changed
python3 manage.py makemigrations
python3 manage.py migrate

#start django application
uwsgi --socket django.sock --module programmeDjango.wsgi --daemonize=log.log

while true; do sleep 1000; done


