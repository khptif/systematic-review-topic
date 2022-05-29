#!/bin/sh
# the script that configure and run the django process

# get options
. ./docker_volume/options.sh

settings_path=programmeDjango/settings.py

# the data to access database
sed -i "s/x_db_name_x/${DB_NAME}/g" $settings_path
sed -i "s/x_db_user_name_x/${DB_USER}/g" $settings_path
sed -i "s/x_db_password_x/${DB_PASSWORD}/g" $settings_path
sed -i "s/x_db_host_x/${DB_HOST}/g" $settings_path

# some global parameters for settings.py
echo NUMBER_THREADS_ALLOWED=${NUMBER_THREADS_ALLOWED} >> $settings_path
echo NUMBER_TRIALS=${NUMBER_TRIALS} >> $settings_path
echo X_INTERVAL_LITTLE=${X_INTERVAL_LITTLE} >> $settings_path
echo Y_INTERVAL_LITTLE=${Y_INTERVAL_LITTLE} >> $settings_path
echo X_INTERVAL_BIG=${X_INTERVAL_BIG} >> $settings_path
echo Y_INTERVAL_BIG=${Y_INTERVAL_BIG} >> $settings_path
echo UPDATE_INTERVAL=${UPDATE_INTERVAL} >> $settings_path


#ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled/django_nginx.conf

# give domaine name of the host in nginx conf file
#sed -i "s/x_domain_name_x/${HOST_DOMAIN}/g" /etc/nginx/sites-available/django_nginx.conf

# start nginx
#/etc/init.d/nginx start

#update the database if table changed
python3 manage.py makemigrations
python3 manage.py migrate

#start django application
#uwsgi --socket django.sock --module programmeDjango.wsgi --daemonize=./docker_volume/log.log
python3 manage.py runserver 127.0.0.1:8000
while true; do sleep 1000; done



