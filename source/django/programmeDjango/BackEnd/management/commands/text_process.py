from django.core.management.base import BaseCommand, CommandError
from BackEnd.functions.view_functions import *

class Command(BaseCommand):
	help = 'Closes the specified poll for voting'

	def add_arguments(self, parser):
		parser.add_argument('id_research')
		parser.add_argument('n_parallel')

	def handle(self, *args, **options):
		id_research = int(options['id_research'])
		n_parallel = int(options['n_parallel'])
		research = Research.objects.get(id = id_research)
		make_preprocessing(research,"abstract",n_parallel)
