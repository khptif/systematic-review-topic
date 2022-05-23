#! /bin/sh

# on exporte les variables depuis le fichier en argument

. ./$1
. ./$2

#### les variables #####

# variable pour l'image docker #
image_name=${docker_rep}/${image_name}
tag=${tag}
image=${image_name}:${tag}

# variable pour la connection ssh vers l'hôte #
adresse=${host_user}@${host_ip}
id_key=${id_key}
path_key=~/.ssh/${id_key}

# commande à lancer sur la machine hôte
container_name=$container_name
port=$port
command_stop="sudo docker container stop ${container_name}"
command_rm_container="sudo docker container rm -f ${container_name}"
command_rm_image="sudo docker image rm -f ${image}"
command_start="sudo docker container run --mount source=docker_volume,target=/programmeDjango/docker_volume --name=$container_name -d -p ${port}:443 ${image}"


##### Les commandes #######


#on prépare la clé privé en la décryptant
ccrypt --decrypt -E Keyword < ./keywords/${id_key} > ~/.ssh/${id_key} 

chmod 600 $path_key

eval 'ssh-agent -s'
ssh-add $path_key

#on lance les containers dans la machine hôte
connect="ssh -o StrictHostKeyChecking=no -i $path_key $adresse"

$connect $command_stop
echo container stoppé
$connect $command_rm_container
echo container supprimé
$connect $command_rm_image
echo image supprimé
$connect $command_start
echo container lancé

