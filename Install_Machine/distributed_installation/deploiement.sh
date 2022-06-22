#! /bin/sh

#### we deploy the software to the host machine ####

# we import variables
. ./parametres_deploiement.sh
. ./parametres_machine.sh

# we download git repository
git clone ${repository_url}

# we create docker image, push it to docker hub et return to main directory
cd ${repository_name}/${path_to_dockerfile}

if [ $UI_Front_deploy==True ];then
	# we save this file before change it
	cp programmeDjango/launch_django.sh ./launch_django.sh
	sed -i "s/x_Module_x/UI_Front/g" programmeDjango/launch_django.sh
	# we build image and push to DockerHub
	docker build -t ${UI_Front_docker_image_name} .
	docker push ${UI_Front_docker_image_name}
	docker image rm ${UI_Front_docker_image_name}
	# we replace the original file
	cp ./launch_django.sh programmeDjango/launch_django.sh
fi

if [ $BackEnd_deploy==True ];then
	# we save this file before change it
	cp programmeDjango/launch_django.sh ./launch_django.sh
	sed -i "s/x_Module_x/BackEnd/g" programmeDjango/launch_django.sh
	# we build image and push to DockerHub
	docker build -t ${BackEnd_docker_image_name} .
	docker push ${BackEnd_docker_image_name}
	docker image rm ${BackEnd_docker_image_name}
	# we replace the original file
	cp ./launch_django.sh programmeDjango/launch_django.sh
fi

if [ $DataBase_deploy==True ];then
	# we save this file before change it
	cp programmeDjango/launch_django.sh ./launch_django.sh
	sed -i "s/x_Module_x/DataBase/g" programmeDjango/launch_django.sh
	# we build image and push to DockerHub
	docker build -t ${DataBase_docker_image_name} .
	docker push ${DataBase_docker_image_name}
	docker image rm ${DataBase_docker_image_name}
	# we replace the original file
	cp ./launch_django.sh programmeDjango/launch_django.sh
fi

cd -

#we delete the local copy of the git repository
rm -Rf ${repository_name}


if [ $UI_Front_deploy==True ];then
#we start container in UI-Front

#we define variables
user_name=${UI_Front_user_name}
host_adresse=${UI_Front_host_adresse}
private_key_path=${UI_Front_private_key_path}
docker_container_name=${UI_Front_docker_container_name}
adresse=${user_name}@${host_adresse}
host_port=${UI_Front_host_port}
docker_image_name=${UI_Front_docker_image_name}

#we connect to host
connect_ssh="ssh -i ${private_key_path} ${adresse}"

#we stop and rm the current container
$connect_ssh "sudo docker container stop ${docker_container_name}"
$connect_ssh "sudo docker container rm ${docker_container_name}"

#we remove the local docker image
$connect_ssh "sudo docker image rm ${docker_image_name}"

#we start the new container
$connect_ssh "sudo docker container run --mount source=docker_volume,target=/programmeDjango/docker_volume --name=${docker_container_name} -d -p ${host_port}:${docker_local_port} ${docker_image_name}
"
fi



if [ $BackEnd_deploy==True ];then
#we start container in UI-Front

#we define variables
user_name=${BackEnd_user_name}
host_adresse=${BackEnd_host_adresse}
private_key_path=${BackEnd_private_key_path}
docker_container_name=${BackEnd_docker_container_name}
adresse=${user_name}@${host_adresse}
host_port=${BackEnd_host_port}
docker_image_name=${BackEnd_docker_image_name}

#we connect to host
connect_ssh="ssh -i ${private_key_path} ${adresse}"

#we stop and rm the current container
$connect_ssh "sudo docker container stop ${docker_container_name}"
$connect_ssh "sudo docker container rm ${docker_container_name}"

#we remove the local docker image
$connect_ssh "sudo docker image rm ${docker_image_name}"

#we start the new container
$connect_ssh "sudo docker container run --mount source=docker_volume,target=/programmeDjango/docker_volume --name=${docker_container_name} -d -p ${host_port}:${docker_local_port} ${docker_image_name}
"
fi



if [ $DataBase_deploy==True ];then
#we start container in UI-Front

#we define variables
user_name=${DataBase_user_name}
host_adresse=${DataBase_host_adresse}
private_key_path=${DataBase_private_key_path}
docker_container_name=${DataBase_docker_container_name}
adresse=${user_name}@${host_adresse}
host_port=${DataBase_host_port}
docker_image_name=${DataBase_docker_image_name}

#we connect to host
connect_ssh="ssh -i ${private_key_path} ${adresse}"

#we stop and rm the current container
$connect_ssh "sudo docker container stop ${docker_container_name}"
$connect_ssh "sudo docker container rm ${docker_container_name}"

#we remove the local docker image
$connect_ssh "sudo docker image rm ${docker_image_name}"

#we start the new container
$connect_ssh "sudo docker container run --mount source=docker_volume,target=/programmeDjango/docker_volume --name=${docker_container_name} -d -p ${host_port}:${docker_local_port} ${docker_image_name}
"
fi



