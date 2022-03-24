#! /bin/sh

. ./parametres_machine.sh

sudo scp -i ${private_key_path} ../docker_install.sh ${user_name}@${host_adresse}:/home/${user_name}/docker_install.sh
sudo ssh -i ${private_key_path} ${user_name}@${host_adresse} "sudo ./docker_install.sh ; "
sudo scp -i ${private_key_path} ../docker_environnment.env ${user_name}@${host_adresse}:/home/${user_name}/docker_environnment.env
