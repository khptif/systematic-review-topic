#! /bin/sh

#### we deploy the software to the host machine ####

# we import variables
. ./parametres_deploiement.sh
. ./parametres_machine.sh

# we download git repository
git clone ${repository_url}

# we create docker image, push it to docker hub et return to main directory
cd ${repository_name}/${path_to_dockerfile}
docker build -t ${docker_image_name} .
docker push ${docker_image_name}
docker image rm ${docker_image_name}
cd -

#we delete the local copy of the git repository
rm -Rf ${repository_name}

#we connect to host
adresse=${user_name}@${host_adresse}
connect_ssh="sudo ssh -i ${private_key_path} ${adresse}"

#we stop and rm the current container
$connect_ssh "sudo docker container stop ${docker_container_name}"
$connect_ssh "sudo docker container rm ${docker_container_name}"

#we remove the local docker image
$connect_ssh "sudo docker image rm ${docker_image_name}"

#we start the new container
$connect_ssh "sudo docker container run --mount source=docker_volume,target=/programmeDjango/docker_volume --name=${docker_container_name} -d -p ${host_port}:${docker_local_port} ${docker_image_name}
"






