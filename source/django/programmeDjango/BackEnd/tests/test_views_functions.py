from django.test import TestCase
from BackEnd.functions.view_functions import *

class test_max_article(TestCase):
    """ Input: string search
        Output: the number of articles you can get at least
        We test to see if the result is more than zero"""

    def test_method(self):
        search = '"vitamine c"'
        self.assertLess(0 , max_article(search))
    

class test_make_research(TestCase):
    """ Input: string search, the research object, the number of thread.
        Output: it writes in database all data from article
        We will compare the max_article and the number of article retrieved"""

    def test_method(self):
        search = '"vitamine c"'
        research = Research.objects.create(search=search)
        total_article = max_article(search)

        make_research(search,research,2)

        # we check if we have at most more than the half of the max article
        self.assertLess(int(total_article/2), Article.objects.filter(research_article__research=research).count())
    

class test_preprocessing_parallel(TestCase):
    """ Input: research object ,articles QuerySet, corpus in ["abstract","full_text","both"] 
        Output: write in database Preprocess_text objects."""

    def test_method(self):
        pass
        