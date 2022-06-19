from django.test import TestCase
from BackEnd.functions.Get_arXiV import *

class test_get_max_article(TestCase):

    def test_method(self):
        input = '"vitamine C"'
        search = get_search_term(input)
        output_expected = 10
        output_result = get_max_article(search)
        self.assertGreaterEqual(output_result,output_expected)

class test_Get_ID(TestCase):

    def test_method(self):
        input = '"vitamine C"'
        search = get_search_term(input)
        research = Research.objects.create()
        output_expected = get_max_article(search)

        list_id = Get_ID(search,research)
        list_page = Article_Job.objects.filter(research=research,type="page").values_list("job",flat=True)

        self.assertGreaterEqual(len(list_id),output_expected)
        self.assertEqual(list_page[0],"0")

class test_extract_article(TestCase):

    def test_method(self):
        input = '1701.08145'
        research = Research.objects.create()
        extract_article([input],research=research)

        list_id = Article_Job.objects.filter(research=research,type="id").values_list("job",flat=True)
        print(list_id)
        article = Article.objects.filter(research_article__research=research)[0]
        print(article.title)