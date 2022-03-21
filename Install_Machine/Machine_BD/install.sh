#! /bin/sh

. ./parametres_machine.sh

. ./parametres_BD.sh


adresse=${user_name}@${host_adresse}
connect_scp="sudo scp -i ${private_key_path}"
connect_ssh="sudo ssh -i ${private_key_path} ${adresse}"
echo $adresse
echo $connect_ssh

# on envoie le fichier script et on installe docker
$connect_scp ../docker_install.sh ${adresse}:/home/${user_name}/docker_install.sh
$connect_ssh "sudo ./docker_install.sh ; "

#on envoie le fichier script et on installe Postgresql et le configure
$connect_scp ./sqlCommand.sh ${adresse}:/home/${user_name}/sqlCommand.sh
$connect_scp ./script.sh ${adresse}:/home/${user_name}/script.sh
$connect_ssh " ./script.sh ${db_name} ${db_user_name} ${password}"

#on envoie les fichiers configuration de postgresql pour qu'il se connecte à l'extérieur

$connect_scp ./pg_hba.conf ${adresse}:/home/${user_name}/pg_hba.conf

$connect_ssh " sudo mv /home/${user_name}/pg_hba.conf /etc/postgresql/12/main/pg_hba.conf"
$connect_ssh " sudo chgrp postgres /etc/postgresql/12/main/pg_hba.conf"
$connect_ssh " sudo chown postgres /etc/postgresql/12/main/pg_hba.conf"

$connect_ssh "sudo service postgresql restart"

