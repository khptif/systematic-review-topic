#!/bin/bash
# the script that configure and run the django process

# in which type of module we are
module_name=x_Module_x

# get options
if [ $module_name == UI_Front ]
then
	. ./docker_volume/UI_Front_options.sh
elif [ $module_name == BackEnd ]
then
	. ./docker_volume/BackEnd_options.sh
elif [ $module_name == DataBase ]
then
	. ./docker_volume/DataBase_options.sh
else	

. ./docker_volume/options.sh
fi

# we add paramters to settings.py
settings_path=programmeDjango/settings.py
# the data to access database
sed -i "s/x_db_name_x/${DB_NAME}/g" $settings_path
sed -i "s/x_db_user_name_x/${DB_USER}/g" $settings_path
sed -i "s/x_db_password_x/${DB_PASSWORD}/g" $settings_path
sed -i "s/x_db_host_x/${DB_HOST}/g" $settings_path

# if this is ssl, we set parameters to redirects http to https
if [ $is_ssl == True ];
then
	echo SECURE_PROXY_SSL_HEADER = \(\'HTTP_X_FORWARDED_PROTO\', \'https\'\) >> $settings_path
	echo SECURE_SSL_REDIRECT = True >> $settings_path
else
	echo SECURE_SSL_REDIRECT = False >> $settings_path
fi

# we give coordinate of each module
if [ $is_decentralised == True ];
then

	echo UI_Front_host_adresse=\"${UI_Front_host_adresse}\" >> $settings_path
	echo UI_Front_host_port=${UI_Front_host_port} >> $settings_path

	echo BackEnd_host_adresse=\"${BackEnd_host_adresse}\" >> $settings_path
	echo BackEnd_host_port=${BackEnd_host_port} >> $settings_path

	echo DataBase_host_adresse=\"${DataBase_host_adresse}\" >> $settings_path
	echo DataBase_host_port=${DataBase_host_port} >> $settings_path

	# we give variable if i a module us ssl
	echo UI_Front_SSL=${UI_Front_SSL} >> $settings_path
	echo BackEnd_SSL=${BackEnd_SSL} >> $settings_path
	echo DataBase_SSL=${DataBase_SSL} >> $settings_path
fi

# some global parameters for settings.py
echo NUMBER_THREADS_ALLOWED=${NUMBER_THREADS_ALLOWED} >> $settings_path
echo NUMBER_TRIALS=${NUMBER_TRIALS} >> $settings_path
echo X_INTERVAL_LITTLE=${X_INTERVAL_LITTLE} >> $settings_path
echo Y_INTERVAL_LITTLE=${Y_INTERVAL_LITTLE} >> $settings_path
echo X_INTERVAL_BIG=${X_INTERVAL_BIG} >> $settings_path
echo Y_INTERVAL_BIG=${Y_INTERVAL_BIG} >> $settings_path
echo UPDATE_INTERVAL=${UPDATE_INTERVAL} >> $settings_path
echo NUMBER_ARTICLE_BY_PAGE=${NUMBER_ARTICLE_BY_PAGE} >> $settings_path
echo is_decentralized=${is_decentralised} >> $settings_path

# we change the urls.py file if this a decentralized module
if [ $module_name == UI_Front ]
then
	cp ./docker_volume/UI_front_urls.py ./programmeDjango/urls.py

elif [ $module_name == BackEnd ]
then
	cp ./docker_volume/BackEnd_urls.py ./programmeDjango/urls.py
elif [ $module_name == DataBase ]
then
	cp ./docker_volume/DataBase_urls.py ./programmeDjango/urls.py
fi

# we replace the nginx file and if SSL is active, we rewrite it

if [ $is_ssl == True ];
then
	cp nginx_config/django_nginx_ssl.conf /etc/nginx/sites-available/django_nginx.conf	
	sed -i "s/x_fullchain.pem_x/${ssl_full_chain}/g" /etc/nginx/sites-available/django_nginx.conf
	sed -i "s/x_privkey.pem_x/${ssl_privkey}/g" /etc/nginx/sites-available/django_nginx.conf
	sed -i "s/x_options-ssl-nginx.conf_x/${ssl_option}/g" /etc/nginx/sites-available/django_nginx.conf
	sed -i "s/x_ssl-dhparams.pem_x/${dhparam}/g" /etc/nginx/sites-available/django_nginx.conf
	sed -i "s/x_domain_name_x/${hostname}/g" /etc/nginx/sites-available/django_nginx.conf

else
	cp nginx_config/django_nginx.conf /etc/nginx/sites-available/django_nginx.conf
fi

ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled/django_nginx.conf

# start nginx
/etc/init.d/nginx start
cat /var/log/nginx/error.log
#install all modules required

python3 -m pip install -r requirements.txt

#update the database if table changed
python3 manage.py makemigrations UI_Front
python3 manage.py makemigrations DataBase
python3 manage.py makemigrations BackEnd
python3 manage.py migrate

#start django application
uwsgi --socket django.sock --module programmeDjango.wsgi --daemonize=./docker_volume/${module_name}_log.log --master --threads ${max_thread}
#python3 manage.py runserver 0.0.0.0:8000

# we have to be in infinity loop so the docker container doesn't stop. 
while true 
do 
sleep 100
# if this is BackEnd module, every 100 seconds, we make "restart_research" request so if a research have stopped, we restart it
if [ $module_name == BackEnd ]
then
	if [ $is_ssl == True ]
	then
		curl https://${BackEnd_host_adresse}:${BackEnd_host_port}/restart_research
	else
		curl http://${BackEnd_host_adresse}:${BackEnd_host_port}/restart_research
	fi
fi
done




