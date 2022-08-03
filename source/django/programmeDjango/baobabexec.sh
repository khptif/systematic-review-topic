#!/bin/bash
# the script execute text processing and clustering in baobab machine
# We have to be in the repertory of this script before execute it

# In Baobab machine, the "source/django/programmeDjango" repertory has to be downloaded.
# We can do it with "git clone url_git_repository". After, we have to create
# virtual environnment for python module with "virtualenv". At the end,
# we download the module with pip -r requirements.txt.

# It takes as argument the id of the research and the number of parallel
# working element we allocate for text processing and clustering

# We can modify the command or argument for text processing and clustering in 
# "BackEnd/management/commands/text_process.py or clustering.py

# id research argument
id_research=$1

# we check if the variable is a number
re='^[0-9]+$'
if ! [[ $id_research =~ $re ]] ; then
   echo "error: The id research given isn't a positive number" >&2; exit 1
fi

# we check if we have a number greater than zero
if [ $id_research -lt 1 ] ; then
	echo "error: The id research given isn't a positive number" >&2; exit 1
fi


# number of parallel element. We define a max number of parallel element for security
n_parallel=$2
max_parallel=10

# we check if the variable is a number
re='^[0-9]+$'
if ! [[ $n_parallel =~ $re ]] ; then
   echo "error: The number of worker unit parallel given isn't a positive number" >&2; exit 1
fi

# if the number is lesser than 1, we assign 1 to the variable
if [ $n_parallel -lt 1 ] ; then
	n_parallel=1
fi
# if the number is greater than the max, we assign the max_parallel
if [ $n_parallel -gt $max_parallel ] ; then
	n_parallel=$max_parallel
fi



# we put virtual environnment.
# The virtual env was create with "virtualenv"

path_to_virtEnv=env_test

source ${path_to_virtEnv}/bin/activate

echo "Text Processing Execution"
# we execute the python script for text processing
python3 manage.py text_process $id_research $n_parallel
echo "Text Processing Finish"

echo "Clustering Execution"
# we execute the python script for clustering.
for index in $(seq 1 $n_parallel)
do
	python3 manage.py clustering $id_research $n_parallel&
done





