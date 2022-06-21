#! /bin/sh

# we create the parameters

# we import variables
. ./config_options.sh
. ./parametres_machine.sh
. ./parametres_BD.sh



# we configure the UI_Front host
# we configure the command
user_name=${UI_Front_user_name}
host_adresse=${UI_Front_host_adresse}
private_key_path=${UI_Front_private_key_path}
adresse=${user_name}@${host_adresse}
connect_scp="sudo scp -i ${private_key_path}"
connect_ssh="sudo ssh -i ${private_key_path} ${adresse}"

# we send the script of docker installation and install docker in host machine
$connect_scp ./docker_install.sh ${adresse}:/home/${user_name}/docker_install.sh
$connect_ssh "./docker_install.sh ; "

# we set some parameter in the option.sh and send to the host
. ./config_options.sh
echo ssl_full_chain=${UI_Front_ssl_full_chain} >> ./${env_file}
echo ssl_privkey=${UI_Front_ssl_privkey} >> ./${env_file}
echo ssl_option=${UI_Front_ssl_option} >> ./${env_file}
echo dhparam=${UI_Front_dhparam} >> ./${env_file}
echo is_ssl=${UI_Front_SSL} >> ./${env_file}
echo hostname=${UI_Front_host_adresse} >> ./${env_file}
echo max_thread=${UI_Front_max_thread} >> ./${env_file}

sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/UI_Front_options.sh
# we send the urls.py file
sudo scp -i ${private_key_path} ../source/django/fichiers_settings/UI_front_urls.py ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/UI_front_urls.py



# we configure the BackEnd host
# we configure the command
user_name=${BackEnd_user_name}
host_adresse=${BackEnd_host_adresse}
private_key_path=${BackEnd_private_key_path}
adresse=${user_name}@${host_adresse}
connect_scp="sudo scp -i ${private_key_path}"
connect_ssh="sudo ssh -i ${private_key_path} ${adresse}"

# we send the script of docker installation and install docker in host machine
$connect_scp ./docker_install.sh ${adresse}:/home/${user_name}/docker_install.sh
$connect_ssh "./docker_install.sh ; "

# we set some parameter in the option.sh and send to the host
. ./config_options.sh
echo ssl_full_chain=${BackEnd_ssl_full_chain} >> ./${env_file}
echo ssl_privkey=${BackEnd_ssl_privkey} >> ./${env_file}
echo ssl_option=${BackEnd_ssl_option} >> ./${env_file}
echo dhparam=${BackEnd_dhparam} >> ./${env_file}
echo is_ssl=${BackEnd_SSL} >> ./${env_file}
echo hostname=${BackEnd_host_adresse} >> ./${env_file}
echo max_thread=${BackEnd_max_thread} >> ./${env_file}

sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/BackEnd_options.sh
# we send the urls.py file
sudo scp -i ${private_key_path} ../source/django/fichiers_settings/BackEnd_urls.py ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/BackEnd_urls.py



# we configure the DataBase host
# we configure the command
user_name=${DataBase_user_name}
host_adresse=${DataBase_host_adresse}
private_key_path=${DataBase_private_key_path}
adresse=${user_name}@${host_adresse}
connect_scp="sudo scp -i ${private_key_path}"
connect_ssh="sudo ssh -i ${private_key_path} ${adresse}"

# we send the script of docker installation and install docker in host machine
$connect_scp ./docker_install.sh ${adresse}:/home/${user_name}/docker_install.sh
$connect_ssh "./docker_install.sh ; "

# we send script for installation of Postgresql database and install it
$connect_scp ./sqlCommand.sh ${adresse}:/home/${user_name}/sqlCommand.sh
$connect_scp ./install_PostGreSQL.sh ${adresse}:/home/${user_name}/install_PostGreSQL.sh
$connect_ssh " ./install_PostGreSQL.sh ${db_name} ${db_user_name} ${password}"

# we configure to let connection to the database

$connect_scp ./pg_hba.conf ${adresse}:/home/${user_name}/pg_hba.conf

$connect_ssh " sudo mv /home/${user_name}/pg_hba.conf /etc/postgresql/12/main/pg_hba.conf"
$connect_ssh " sudo chgrp postgres /etc/postgresql/12/main/pg_hba.conf"
$connect_ssh " sudo chown postgres /etc/postgresql/12/main/pg_hba.conf"

$connect_ssh "sudo service postgresql restart"

# we set some unique parameter for the module in the option.sh and send to the host
. ./config_options.sh
echo ssl_full_chain=${DataBase_ssl_full_chain} >> ./${env_file}
echo ssl_privkey=${DataBase_ssl_privkey} >> ./${env_file}
echo ssl_option=${DataBase_ssl_option} >> ./${env_file}
echo dhparam=${DataBase_dhparam} >> ./${env_file}
echo is_ssl=${DataBase_SSL} >> ./${env_file}
echo hostname=${DataBase_host_adresse} >> ./${env_file}
echo max_thread=${DataBase_max_thread} >> ./${env_file}

sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/DataBase_options.sh
# we send the urls.py file
sudo scp -i ${private_key_path} ../source/django/fichiers_settings/DataBase_urls.py ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/DataBase_urls.py


