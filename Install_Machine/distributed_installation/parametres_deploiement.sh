#! /bin/sh

export repository_name=systematic-review-topic
export repository_url=https://github.com/khptif/systematic-review-topic
export path_to_dockerfile=source/django

export UI_Front_docker_image_name=khptif/ui_front_systematic_review:latest
export BackEnd_docker_image_name=khptif/backend_systematic_review:latest
export DataBase_docker_image_name=khptif/database_systematic_review:latest

export UI_Front_docker_container_name=ui_front_systematic
export BackEnd_docker_container_name=backend_systematic
export DataBase_docker_container_name=database_systematic

export UI_Front_deploy=True
export BackEnd_deploy=True
export DataBase_deploy=True

#export docker_local_port=443
export docker_local_port=8000

