#! /bin/sh

# we build the options file
. ./config_options.sh
env_file=options.sh

# we configure DataBase Host
cd Machine_BD
. ./parametres_machine.sh
. ./parametres_BD.sh
./install.sh
cd ..


echo IS_DATABASE=${is_database} >> $env_file
echo IS_BACKEND=${is_backend} >> $env_file
echo IS_FRONTEND=${is_frontend} >> $env_file
sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/${env_file}


# we configure FrontEnd Host
. ./config_options.sh
cd Machine_Front
. ./parametres_machine.sh
./install.sh
cd ..

echo IS_DATABASE=${is_database} >> $env_file
echo IS_BACKEND=${is_backend} >> $env_file
echo IS_FRONTEND=${is_frontend} >> $env_file
sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/${env_file}


# we configure BackEnd Host
. ./config_options.sh
cd Machine_Back
. ./parametres_machine.sh
./install.sh
cd ..

echo IS_DATABASE=${is_database} >> $env_file
echo IS_BACKEND=${is_backend} >> $env_file
echo IS_FRONTEND=${is_frontend} >> $env_file
sudo scp -i ${private_key_path} ./${env_file} ${user_name}@${host_adresse}:/home/${user_name}/docker_volume/${env_file}



