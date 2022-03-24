#! /bin/sh

docker build -t khptif/UI-Front:latest .

echo ${docker_password} | docker login --username ${docker_user} --password-stdin

docker push khptif/UI-Front:latest

echo ${UI_Front_key} > id_key

command_stop="sudo docker container stop ui_front"
command_rm="sudo docker rm -f khptif/UI-Front:latest"
command_start="sudo docker container run --env-file=docker_environnment.env --name=ui_front -d -p 8000:8000 khptif/UI-Front:latest"

adresse=${machine_front_user}@${machine_front_ip}

echo yes | ssh -i id_key $adresse $command_stop
ssh -i id_key $adresse $command_rm
ssh -i id_key $adresse $command_start
