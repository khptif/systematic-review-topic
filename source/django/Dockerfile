FROM nginx:1.20.2

RUN apt-get -y update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install python3-psycopg2

RUN python3 -m pip install django
RUN python3 -m pip install uwsgi
RUN python3 -m pip install psycopg2-binary


COPY programmeDjango/ .
COPY django_nginx.conf /etc/nginx/sites-available/django_nginx.conf

RUN ln -s /etc/nginx/sites-available/django_nginx.conf /etc/nginx/sites-enabled
RUN cp /etc/nginx/uwsgi_params /programmeDjango/uwsgi_params
RUN cd programmeDjango
EXPOSE 8000

RUN /etc/init.d/nginx start

CMD ./launch_django.sh ${DB_NAME} ${DB_USER} ${DB_PASSWORD} ${DB_HOST} 



