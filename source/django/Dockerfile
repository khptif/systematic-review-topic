FROM ubuntu:20.04

RUN apt-get -y update
RUN apt-get -y install apt-utils
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get -y install nginx


COPY programmeDjango/ ./programmeDjango/
WORKDIR programmeDjango

COPY fichiers_settings/settings.py programmeDjango/settings.py
COPY fichiers_settings/ ./fichiers_settings/
COPY nginx_config/ ./nginx_config/

CMD ./launch_django.sh 



