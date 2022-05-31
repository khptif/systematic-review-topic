#! /bin/sh

# on exporte les variables depuis le fichier en argument

. ./$1
. ./$2
#### les variables #####


# variable pour la connection ssh vers l'hôte #
adresse=${host_user}@${host_ip}
id_key=${id_key}
path_key=~/.ssh/${id_key}

directory="/home/ubuntu/systematic"


#on prépare la clé privé en la décryptant
ccrypt --decrypt -E Keyword < ./keywords/${id_key} > ~/.ssh/${id_key} 

chmod 600 $path_key

eval 'ssh-agent -s'
ssh-add $path_key

#on lance les containers dans la machine hôte
connect="ssh -o StrictHostKeyChecking=no -i $path_key $adresse"
connect_copy="scp -o StrictHostKeyChecking=no -i $path_key $adresse"

copy_directory="-r ../source/django/programmeDjango $adresse:/home/${host_user}
##### Les commandes #######




$connect $command_stop
echo container stoppé
$connect $command_rm_container
echo container supprimé
$connect $command_rm_image
echo image supprimé
$connect $command_start
echo container lancé

