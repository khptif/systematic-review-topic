from django.core.management.base import BaseCommand, CommandError
from BackEnd.functions.view_functions import *
from programmeDjango.settings import NUMBER_TRIALS

class Command(BaseCommand):
	help = 'Closes the specified poll for voting'

	def add_arguments(self, parser):
		parser.add_argument('id_research')
		parser.add_argument('n_parallel')

	def handle(self, *args, **options):
		id_research = int(options['id_research'])
		n_parallel = int(options['n_parallel'])
		number_trials = int(NUMBER_TRIALS / n_parallel) + 1
		research = Research.objects.get(id=id_research)

		print_research("Clustering Step begin",research.id)
		print_research("Recuperate temporary file if don't exist",research.id)
        # if the tf_idf and other data are null, we charge them from save files
		
		tf_idf = joblib.load(f"{TEMPORARY_DATA}/tf_idf_research_{str(research.id)}.pkl")
		
		id_list = joblib.load(f"{TEMPORARY_DATA}/id_list_research_{str(research.id)}.pkl")
		
		final_list = joblib.load(f"{TEMPORARY_DATA}/final_list_research_{str(research.id)}.pkl")

		print_research("Clusterin begin",research.id)
		make_cluster(research,id_list,final_list,tf_idf,number_trials,1)
		print_research("Clusterin end",research.id)
		
