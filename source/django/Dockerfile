FROM ubuntu:20.04

RUN apt-get -y update
RUN apt-get -y install python3.9
RUN apt-get -y install python3-pip
RUN apt-get -y install python3-psycopg2
RUN apt-get -y install nginx


COPY django_nginx.conf /etc/nginx/sites-available/django_nginx.conf
RUN ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled/


COPY programmeDjango/ ./programmeDjango/


RUN python3 -m pip install -r programmeDjango/requirements.txt

WORKDIR programmeDjango
COPY fichiers_settings/settings.py programmeDjango/settings.py
COPY fichiers_settings/ ./fichiers_settings/
COPY nginx_config/ ./nginx_config/

CMD ./launch_django.sh 



