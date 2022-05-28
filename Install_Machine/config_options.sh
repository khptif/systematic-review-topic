#!/bin/sh

#we create the file options.sh

env_file=options.sh

# we create the file
> $env_file

# we fill the file with parameters of each element
# UI-FRONT parameters
cd Machine_Front
. ./parametres_machine.sh
cd ..
echo UI_FRONT_HOST=${host_adresse} >> $env_file
echo UI_FRONT_PORT=${host_port} >> $env_file
echo HOST_DOMAIN=${host_domain} >> $env_file


# Backend parameters
cd Machine_Back
. ./parametres_machine.sh
cd ..
echo BACKEND_HOST=${host_adresse} >> $env_file
echo BACKEND_PORT=${host_port} >> $env_file

# DataBase parameters
cd Machine_BD
. ./parametres_machine.sh
cd ..
echo DB_NAME=${db_name} >> $env_file
echo DB_USER=${db_user_name} >> $env_file
echo DB_PASSWORD=${password} >> $env_file
echo DB_HOST=${host_adresse} >> $env_file
echo DATABASE_HOST=${host_adresse} >> $env_file
echo DATABASE_PORT=${host_port} >> $env_file


cd Machine_Mono
. ./parametres_machine.sh
cd ..


# we fill the file with the settings parameters for settings.py
. ./settings_parameters.sh
echo NUMBER_THREADS_ALLOWED=${NUMBER_THREADS_ALLOWED} >> $env_file
echo NUMBER_TRIALS=${NUMBER_TRIALS} >> $env_file
echo X_INTERVAL_LITTLE=${X_INTERVAL_LITTLE} >> $env_file
echo Y_INTERVAL_LITTLE=${Y_INTERVAL_LITTLE} >> $env_file
echo X_INTERVAL_BIG=${X_INTERVAL_BIG} >> $env_file
echo Y_INTERVAL_BIG=${Y_INTERVAL_BIG} >> $env_file
echo UPDATE_INTERVAL=${UPDATE_INTERVAL} >> $env_file


