#! /bin/bash

. ./versions.sh


###  Le fichier requirements.txt ####

file=requirements.txt

module=("psycopg2_binary" "uWSGI" "pytest" "coverage" "django_oauth_toolkit" )
version=("$psycopg2_binary" "$uWSGI" "$pytest" "$coverage" "$django_oauth_toolkit" )

echo > $file

for i in ${!module[@]}; do
 echo ${module[$i]}==${version[$i]} >> $file
 
done
