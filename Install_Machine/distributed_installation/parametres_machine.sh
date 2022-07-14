#! /bin/sh


#### UI-FRONT HOST PARAMETERS ##### 

export UI_Front_user_name=ubuntu
export UI_Front_host_adresse=test-ssl.systematic-review-topic-test.ch
export UI_Front_private_key_path=/home/fatih/.ssh/id_front2
export UI_Front_host_port=8000
export UI_Front_max_thread=4

export UI_Front_SSL=True

export UI_Front_ssl_full_chain=fullchain.pem
export UI_Front_ssl_privkey=privkey.pem
export UI_Front_ssl_option=options-ssl-nginx.conf
export UI_Front_dhparam=ssl-dhparams.pem


#### BACKEND HOST PARAMETERS ##### 

export BackEnd_user_name=centos
export BackEnd_host_adresse=195.15.243.204
export BackEnd_private_key_path=/home/fatih/.ssh/id_back2
export BackEnd_host_port=8000
export BackEnd_max_thread=8

export BackEnd_SSL=False

export BackEnd_ssl_full_chain=fullchain.pem
export BackEnd_ssl_privkey=privkey.pem
export BackEnd_ssl_option=options-ssl-nginx.conf
export BackEnd_dhparam=ssl-dhparams.pem


#### DATABASE HOST PARAMETERS ##### 

export DataBase_user_name=ubuntu
export DataBase_host_adresse=test-ssl.systematic-review-topic-test.ch
export DataBase_private_key_path=/home/fatih/.ssh/id_front2
export DataBase_host_port=8001
export DataBase_max_thread=4

export DataBase_SSL=True

export DataBase_ssl_full_chain=fullchain.pem
export DataBase_ssl_privkey=privkey.pem
export DataBase_ssl_option=options-ssl-nginx.conf
export DataBase_dhparam=ssl-dhparams.pem

## email for certbot certification SSL ##
export Email_SSL=fatih_1894@hotmail.com


