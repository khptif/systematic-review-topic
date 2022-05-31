FROM ubuntu:20.04

RUN apt-get -y update
RUN apt-get -y install python3.8
RUN apt-get -y install python3-pip


COPY programmeDjango/requirements.txt ./programmeDjango/requirements.txt

RUN python3 -m pip install -r programmeDjango/requirements.txt


COPY programmeDjango/ ./programmeDjango/
WORKDIR programmeDjango

COPY fichiers_settings/settings.py programmeDjango/settings.py
COPY fichiers_settings/ ./fichiers_settings/
COPY nginx_config/ ./nginx_config/

CMD ./launch_django.sh 



