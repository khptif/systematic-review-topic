#! /bin/sh

# ce script permet de déployer tous les modules nécessaires.
# Il doit être lancé en se trouvant dans son répertoire.

# répertoire des scripts de déploiement
scripts=deploy_scripts

# pour déployer un module, il faut lancer le script 'module_deploy.sh' et lui fournir en argument
# le script avec les paramètres du module

# create and push docker image
./$scripts/docker_image_push.sh $scripts/docker_image_param.sh

# run the container
./$scripts/deploy_container.sh $scripts/machine_param.sh $scripts/docker_image_param.sh


