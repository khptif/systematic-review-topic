#! /bin/sh

# on exporte les variables depuis le fichier en argument

. ./$1

#### les variables #####

# variable pour l'image docker #
image_name=${docker_rep}/${image_name}
tag=${tag}
image=${image_name}:${tag}


##### Les commandes #######

#on construit l'image docker et push vers docker hub
sudo docker build -t $image ../source/django

echo ${docker_password} | docker login --username ${docker_user} --password-stdin

sudo docker push $image




