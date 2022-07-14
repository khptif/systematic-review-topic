#!/bin/bash

DOMAIN=$1
EMAIL=$2

## we install with certbot a certification SSL for Nginx and we copy the certificate
## to docker_volume for the container

# we check if this is a debian based OS or redhat based
if [ -f "/etc/debian_version" ]
then

DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
sudo apt-get update -y
sudo apt-get -y install nginx -y
sudo apt-get remove certbot -y

else

sudo yum install epel-release -y
sudo yum update -y
sudo yum install nginx -y
sudo yum remove certbot -y

fi

sudo systemctl enable nginx
sudo systemctl start nginx

sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

sudo certbot --nginx -n -m $EMAIL --agree-tos -d $DOMAIN

sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem       docker_volume/fullchain.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem         docker_volume/privkey.pem
sudo cp /etc/letsencrypt/options-ssl-nginx.conf           docker_volume/options-ssl-nginx.conf
sudo cp /etc/letsencrypt/ssl-dhparams.pem                 docker_volume/ssl-dhparams.pem
