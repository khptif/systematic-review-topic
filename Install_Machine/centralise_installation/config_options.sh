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
echo is_decentralised=False >> $env_file
echo SSL=${SSL} >> $env_file
echo max_thread=${max_thread} >> $env_file

echo ssl_full_chain=${ssl_full_chain}  >> $env_file
echo ssl_privkey=${ssl_privkey} >> $env_file
echo ssl_option=${ssl_option} >> $env_file
echo dhparam=${dhparam} >> $env_file

