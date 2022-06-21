#! /bin/sh


#### UI-FRONT HOST PARAMETERS ##### 

export UI_Front_user_name=ubuntu
export UI_Front_host_adresse=195.15.243.254
export UI_Front_private_key_path=/home/fatih/.ssh/id_machine
export UI_Front_host_port=8000
export UI_Front_max_thread=4

export UI_Front_ssl_full_chain=UI_Front_fullchain.pem
export UI_Front_ssl_privkey=UI_Front_privkey.pem
export UI_Front_ssl_option=UI_Front_options_ssl_nginx.conf
export UI_Front_dhparam=UI_Front_ssl_dhparams.pem


#### BACKEND HOST PARAMETERS ##### 

export BackEnd_user_name=ubuntu
export BackEnd_host_adresse=195.15.243.254
export BackEnd_private_key_path=/home/fatih/.ssh/id_machine
export BackEnd_host_port=8000
export BackEnd_max_thread=4

export BackEnd_ssl_full_chain=BackEnd_fullchain.pem
export BackEnd_ssl_privkey=BackEnd_privkey.pem
export BackEnd_ssl_option=BackEnd_options_ssl_nginx.conf
export BackEnd_dhparam=BackEnd_ssl_dhparams.pem


#### DATABASE HOST PARAMETERS ##### 

export DataBase_user_name=ubuntu
export DataBase_host_adresse=195.15.243.254
export DataBase_private_key_path=/home/fatih/.ssh/id_machine
export DataBase_host_port=8000
export DataBase_max_thread=4

export DataBase_ssl_full_chain=DataBase_fullchain.pem
export DataBase_ssl_privkey=DataBase_privkey.pem
export DataBase_ssl_option=DataBase_options_ssl_nginx.conf
export DataBase_dhparam=DataBase_ssl_dhparams.pem
