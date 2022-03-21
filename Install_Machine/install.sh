#! /bin/sh

# on définit l'environnement pour ce script

env_file=docker_environnment.env
mv_env="sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/${env_file}"

# on construit le fichier environnement pour les containers dockers
cd Machine_BD
. ./parametres_machine.sh
. ./parametres_BD.sh
cd ..

> $env_file
echo DB_NAME=${db_name} >> $env_file
echo DB_USER=${db_user_name} >> $env_file
echo DB_PASSWORD=${password} >> $env_file
echo DB_HOST=${host_adresse} >> $env_file

# on configure la machine base de donnée
cd Machine_BD
. ./parametres_machine.sh
. ./parametres_BD.sh
./install.sh
cd ..

sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/${env_file}

# on configure la machine front

cd Machine_Front
. ./parametres_machine.sh
./install.sh
cd ..

sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/${env_file}

# on configure la machine back

cd Machine_Back
. ./parametres_machine.sh
./install.sh
cd ..

sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/${env_file}


