#!/bin/sh

#we create the file options.sh

env_file=options.sh

# we create the file
> $env_file

# DataBase parameters
. ./parametres_BD.sh
. ./parametres_machine.sh

echo DB_NAME=${db_name} >> $env_file
echo DB_USER=${db_user_name} >> $env_file
echo DB_PASSWORD=${password} >> $env_file
echo DB_HOST=${host_adresse} >> $env_file

# we fill the file with the settings parameters for settings.py
. ./parametres_settings.sh
echo NUMBER_THREADS_ALLOWED=${NUMBER_THREADS_ALLOWED} >> $env_file
echo NUMBER_TRIALS=${NUMBER_TRIALS} >> $env_file
echo X_INTERVAL_LITTLE=${X_INTERVAL_LITTLE} >> $env_file
echo Y_INTERVAL_LITTLE=${Y_INTERVAL_LITTLE} >> $env_file
echo X_INTERVAL_BIG=${X_INTERVAL_BIG} >> $env_file
echo Y_INTERVAL_BIG=${Y_INTERVAL_BIG} >> $env_file
echo UPDATE_INTERVAL=${UPDATE_INTERVAL} >> $env_file
echo NUMBER_ARTICLE_BY_PAGE=${NUMBER_ARTICLE_BY_PAGE} >> $env_file

# we fill the variable that check if installation is centralised or not
echo is_decentralised=True >> $env_file

# we fill the variable with host name or ip of each host and port

echo UI_Front_host_adresse=${UI_Front_host_adresse} >> $env_file
echo UI_Front_host_port=${UI_Front_host_port} >> $env_file

echo BackEnd_host_adresse=${BackEnd_host_adresse} >> $env_file
echo BackEnd_host_port=${BackEnd_host_port} >> $env_file

echo DataBase_host_adresse=${DataBase_host_adresse} >> $env_file
echo DataBase_host_port=${DataBase_host_port} >> $env_file

#we fill the variable that check if SSL is set or not on host
echo UI_Front_SSL=${UI_Front_SSL} >> $env_file
echo BackEnd_SSL=${BackEnd_SSL} >> $env_file
echo DataBase_SSL=${DataBase_SSL} >> $env_file


