#!/bin/bash

# we check if this is a debian based OS or redhat based
if [ -f "/etc/debian_version" ]
then

# we install docker in the host
sudo apt-get remove docker docker-engine docker.io containerd runc

sudo apt-get update
sudo apt-get -y install ca-certificates curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  
sudo apt-get update
sudo apt-get -y install docker-ce docker-ce-cli containerd.io

# we create a repertory who will be a docker volume
path_to_docker_volume=$(pwd)/docker_volume
mkdir $path_to_docker_volume
mkdir $path_to_docker_volume/data
mkdir $path_to_docker_volume/articles
mkdir $path_to_docker_volume/plot

sudo docker volume create --name docker_volume --opt type=none --opt device=$path_to_docker_volume --opt o=bind

else

sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine
                  

sudo yum -y install -y yum-utils
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
    
sudo yum -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker

# we create a repertory who will be a docker volume
path_to_docker_volume=$(pwd)/docker_volume
mkdir $path_to_docker_volume
mkdir $path_to_docker_volume/data
mkdir $path_to_docker_volume/articles
mkdir $path_to_docker_volume/plot

sudo docker volume create --name docker_volume --opt type=none --opt device=$path_to_docker_volume --opt o=bind

fi
