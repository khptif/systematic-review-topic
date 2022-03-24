#! /bin/sh

# ce script permet de déployer tous les modules nécessaires.
# Il doit être lancé en se trouvant dans son répertoire.

# répertoire des scripts de déploiement
scripts=deploy_scripts

# pour déployer un module, il faut lancer le script 'module_deploy.sh' et lui fournir en argument
# le script avec les paramètres du module

#module UI_FRONT
./$scripts/module_deploy.sh $scripts/ui_front_param.sh
