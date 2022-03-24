#! /bin/sh

#### les variables #####

# variable pour l'image docker #
image_name=khptif/ui-front
tag=latest
image=${image_name}:${tag}

# variable pour la connection ssh vers l'hôte #
adresse=${machine_front_user}@${machine_front_ip}
id_key=id_machine_front

# commande à lancer sur la machine hôte
command_stop="sudo docker container stop ui_front"
command_rm="sudo docker rm -f ${image}"
command_start="sudo docker container run --env-file=docker_environnment.env --name=ui_front -d -p 8000:8000 ${image}"


##### Les commandes #######

#on construit l'image docker et push vers docker hub
docker build -t $image .

echo ${docker_password} | docker login --username ${docker_user} --password-stdin

docker push $image


#on prépare la clé privé en la décryptant
ccrypt --decrypt -E keyword < travis-script/keywords/${id_key} > ~/.ssh/${id_key} 

chmod 600 ~/.ssh/$id_key

eval 'ssh-agent -s'
ssh-add ~/.ssh/${id_key}

#on lance les containers dans la machine hôte
ssh -o StrictHostKeyChecking=no -i $id_key $adresse $command_stop
ssh -o StrictHostKeyChecking=no -i $id_key $adresse $command_rm
ssh -o StrictHostKeyChecking=no -i $id_key $adresse $command_start
