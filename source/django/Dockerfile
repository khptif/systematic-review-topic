FROM ubuntu:20.04

RUN apt-get -y update
RUN apt-get -y install python3.9
RUN apt-get -y install python3-pip
RUN apt-get -y install python3-psycopg2

COPY programmeDjango/ ./programmeDjango/

RUN python3 -m pip install -r programmeDjango/requirements.txt

COPY django_nginx.conf /etc/nginx/sites-available/django_nginx.conf
COPY fichiers_settings/settings.py .

RUN cp settings.py programmeDjango/programmeDjango/settings.py

WORKDIR programmeDjango

EXPOSE 8000

CMD ./launch_django.sh ${DB_NAME} ${DB_USER} ${DB_PASSWORD} ${DB_HOST} 



