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

# we write the adresse of other host in settings.py
echo UI_FRONT_HOST="'${UI_FRONT_HOST}'" >> $settings_path
echo UI_FRONT_PORT="'${UI_FRONT_PORT}'" >> $settings_path
echo BACKEND_HOST="'${BACKEND_HOST}'" >> $settings_path
echo BACKEND_PORT="'${BACKEND_PORT}'" >> $settings_path
echo DATABASE_HOST="'${DATABASE_HOST}'" >> $settings_path
echo DATABASE_PORT="'${DATABASE_PORT}'" >> $settings_path

# some global parameters for settings.py
echo NUMBER_THREADS_ALLOWED=${NUMBER_THREADS_ALLOWED} >> $settings_path
echo NUMBER_TRIALS=${NUMBER_TRIALS} >> $settings_path
echo X_INTERVAL_LITTLE=${X_INTERVAL_LITTLE} >> $settings_path
echo Y_INTERVAL_LITTLE=${Y_INTERVAL_LITTLE} >> $settings_path
echo X_INTERVAL_BIG=${X_INTERVAL_BIG} >> $settings_path
echo Y_INTERVAL_BIG=${Y_INTERVAL_BIG} >> $settings_path
echo UPDATE_INTERVAL=${UPDATE_INTERVAL} >> $settings_path

# parameters to know the role
echo IS_DATABASE=${IS_DATABASE} >> $settings_path
echo IS_BACKEND=${IS_BACKEND} >> $settings_path
echo IS_FRONTEND=${IS_FRONTEND} >> $settings_path



# according to the role assigned, we give the right files
if test ${IS_DATABASE} = True
then
	cp fichiers_settings/database/urls.py programmeDjango/urls.py
	cp nginx_config/database/django_nginx.conf /etc/nginx/sites-available/django_nginx.conf
	
elif test ${IS_BACKEND} = True
then
	cp fichiers_settings/backend/urls.py programmeDjango/urls.py
	cp nginx_config/backend/django_nginx.conf /etc/nginx/sites-available/django_nginx.conf
elif test ${IS_FRONTEND} = True
then
	cp fichiers_settings/frontend/urls.py programmeDjango/urls.py
	cp nginx_config/frontend/django_nginx.conf /etc/nginx/sites-available/django_nginx.conf
fi

ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled/
cat /etc/nginx/sites-available/django_nginx.conf

# give domaine name of the host in nginx conf file
sed -i "s/x_domain_name_x/${HOST_DOMAIN}/g" /etc/nginx/sites-available/django_nginx.conf

# start nginx
/etc/init.d/nginx start

#update the database if table changed
python3 manage.py makemigrations
python3 manage.py migrate

if test ${IS_BACKEND} = True
then
	python3 manage.py runserver localhost:8000 >> ./docker_volume/test_runserv
elif test ${IS_BACKEND} != True
then
#start django application
uwsgi --socket django.sock --module programmeDjango.wsgi --daemonize=./docker_volume/log.log

while true; do sleep 1000; done

fi


