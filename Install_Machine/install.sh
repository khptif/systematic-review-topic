#! /bin/sh

# we create the parameters

# we import variables
. ./config_options.sh
. ./parametres_machine.sh
. ./parametres_BD.sh

# we configure the command
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

# we send the option.sh to the host
sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/${env_file}




