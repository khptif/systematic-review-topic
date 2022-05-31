FROM ubuntu:20.04

RUN apt-get -y update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip


COPY programmeDjango/ ./programmeDjango/
WORKDIR programmeDjango

COPY fichiers_settings/settings.py programmeDjango/settings.py
COPY fichiers_settings/ ./fichiers_settings/
COPY nginx_config/ ./nginx_config/

CMD ./launch_django.sh 



