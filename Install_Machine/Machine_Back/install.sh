#! /bin/sh

. ./parametres_machine.sh
# we install docker in the host
sudo scp -i ${private_key_path} ../docker_install.sh ${user_name}@${host_adresse}:/home/${user_name}/docker_install.sh
sudo ssh -i ${private_key_path} ${user_name}@${host_adresse} "./docker_install.sh ; "


