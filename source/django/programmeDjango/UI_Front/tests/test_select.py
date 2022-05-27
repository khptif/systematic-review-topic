from ast import keyword
from django.test import TestCase
from UI_Front.functions.select_functions import *


class test_filters_manager(TestCase):
    """ We separatly test each type of value between 'topic','author','keyword' and 'neighbour'.
        And the last test is with all of them together"""

    def test_topic_value(self):
        """ We test with two input for test the topic entry. One who is correct and the other incorrect.
            We test too if the the name topic is good"""
        
        topic = "qwertQWERT, qw-ew12 , lpogkLPF_123XCS"
        input_correct = {"filter_0_1" : ["Type:topic;topic_name:{topic}".format(topic=topic)]}
        input_incorrect = {"flter_0_1" : ["Type:topic;topic_name:{topic}".format(topic=topic)]}

        output_correct_expected = {"filter_0" : {"topic":[topic]}}
        output_incorrect_expected = {}

        output_correct_result = filters_manager(False,input_correct)
        output_incorrect_result = filters_manager(False,input_incorrect)

        self.assertEqual(output_correct_expected,output_correct_result)
        self.assertEqual(output_incorrect_expected,output_incorrect_result)

    def test_author(self):
        """ we give three authors. The two first have the same last name and the two last have the same first name.
            We test with names of the second author.
            We make 3 test: last name only, first name only and the both."""

        #mock authors
        author1 = Author.objects.create(last_name ="Lefebvre",first_name="Antoine")
        author2 = Author.objects.create(last_name ="Lefebvre",first_name="Pierre")
        author3 = Author.objects.create(last_name ="Ratier",first_name="Pierre")

        #inputs
        input1 = {"filter_0_1" : ["Type:author;last_name:Lefebvre;first_name:;"]}
        input2 = {"filter_0_1" : ["Type:author;last_name:;first_name:Pierre;"]}
        input3 = {"filter_0_1" : ["Type:author;last_name:Lefebvre;first_name:Pierre;"]}

        output1_expected = [author1,author2]
        output2_expected = [author2,author3]
        output3_expected = [author2,author3]

        output1_result = filters_manager(False,input1)['filter_0']['author']
        output2_result = filters_manager(False,input2)['filter_0']['author']
        output3_result = filters_manager(False,input3)['filter_0']['author']

        for a in output1_expected:
            self.assertIn(a,output1_result)
        for a in output2_expected:
            self.assertIn(a,output2_result)
        for a in output3_expected:
            self.assertIn(a,output3_result)

    def test_keyword(self):
        """ we give three keywords and check if result is correct"""
        keyword1="TesT1_"
        keyword2="tE-St2_"
        keyword3="TE ST 3"

        input = {"filter_0_1": ["Type:keyword;keyword:{key};".format(key=keyword1),
                                "Type:keyword;keyword:{key};".format(key=keyword2),
                                "Type:keyword;keyword:{key};".format(key=keyword3)]}
        
        output_expected = {"filter_0":{"keyword":[keyword1,keyword2,keyword3]}}
        output_result = filters_manager(False,input)

        self.assertEqual(output_result,output_expected)

    def test_neighbour(self):
        """ we create an article with the doi and check if we obtain this article"""
        doi = "1234"
        article = Article.objects.create(doi=doi)
        input = {"filter_0_1": ["Type:neighbour;DOI:{doi};".format(doi=doi)]}
        output_expected = {"filter_0":{"neighbour":[article]}}