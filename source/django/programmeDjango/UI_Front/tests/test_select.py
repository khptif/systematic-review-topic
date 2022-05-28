from ast import keyword
from django.test import TestCase
from matplotlib.pyplot import title
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
        output_result = filters_manager(False,input)
        self.assertEqual(output_expected,output_result)

    def test_alltogether(self):
        topic="topic_test"

        last_name="test1"
        first_name="test2"
        author=Author.objects.create(last_name=last_name,first_name=first_name)

        keyword = "key_test"

        doi = "1234"
        article = Article.objects.create(doi=doi)

        input = {   "filter_0_1": ["Type:topic;topic_name:{topic}".format(topic=topic)],
                    "filter_0_2":["Type:author;last_name:{last_name};first_name:{first_name};".format(last_name=last_name,first_name=first_name)],
                    "filter_0_3":["Type:keyword;keyword:{key};".format(key=keyword)],
                    "filter_0_4" :["Type:neighbour;DOI:{doi};".format(doi=doi)]}

        output_expected = {"filter_0" : {"topic":[topic],"author":[author],"keyword":[keyword],"neighbour":[article]}}
        output_result = filters_manager(False,input)
        self.assertEqual(output_expected,output_result)

    def test_alltogether_2_filter(self):
        """ we add a supplementary filter and test the same way than "test_alltogether"""

        topic="topic_test"

        last_name="test1"
        first_name="test2"
        author=Author.objects.create(last_name=last_name,first_name=first_name)

        keyword = "key_test"

        doi = "1234"
        article = Article.objects.create(doi=doi)

        input = {   "filter_0_1": ["Type:topic;topic_name:{topic}".format(topic=topic)],
                    "filter_0_2":["Type:author;last_name:{last_name};first_name:{first_name};".format(last_name=last_name,first_name=first_name)],
                    "filter_0_3":["Type:keyword;keyword:{key};".format(key=keyword)],
                    "filter_0_4" :["Type:neighbour;DOI:{doi};".format(doi=doi)],

                    "filter_1_1": ["Type:topic;topic_name:{topic}".format(topic=topic)],
                    "filter_1_2":["Type:author;last_name:{last_name};first_name:{first_name};".format(last_name=last_name,first_name=first_name)],
                    "filter_1_3":["Type:keyword;keyword:{key};".format(key=keyword)],
                    "filter_1_4" :["Type:neighbour;DOI:{doi};".format(doi=doi)]}

        output_expected = { "filter_0" : {"topic":[topic],"author":[author],"keyword":[keyword],"neighbour":[article]},
                            "filter_1" : {"topic":[topic],"author":[author],"keyword":[keyword],"neighbour":[article]}}
        output_result = filters_manager(False,input)
        self.assertEqual(output_expected,output_result)

class test_get_Articles_Filtered(TestCase):

    def test_topic(self):
        """We test if we get the article of a topic and if the article are from the right topic"""
        research = Research.objects.create()
        topic = "topic1"
        topic_other = ["topic2","topic3","topic4"]
        article_in_topic = []
        article_not_in_topic = []
        for i in range(5):
            article_in_topic.append(Article.objects.create())
            article_not_in_topic.append(Article.objects.create())
        #we create the cluster for the topic
        for article in article_in_topic:
            Cluster.objects.create(article=article,pos_x=0,pos_y=0,topic=topic,research=research)
        #we create the cluster for other topic
        import random
        n_other_topic = len(topic_other)
        for article in article_not_in_topic:
            Cluster.objects.create(article=article,pos_x=0,pos_y=0,topic=topic_other[random.randint(0,n_other_topic-1)],research=research)
        
        # we define input
        input = {"filter_0":{"topic":[topic]}}
        output_result = get_Articles_Filtered(research,input)

        #we check if we have the good article
        for article in article_in_topic:
            self.assertIn(article,output_result)
        for article in article_not_in_topic:
            self.assertNotIn(article,output_result)
        
    def test_author(self):
        """We test if get the article written by authors."""
        import random
        research = Research.objects.create()
        
        #we create a list of author that are in input
        author_list = []
        for i in range(3):
            author_list.append(Author.objects.create())
        
        #we create a list of author that aren't in input
        author_not_list = []
        for i in range(3):
            author_not_list.append(Author.objects.create())

        # input test
        input = {"filter_0":{"author":author_list}}

        # we create a number of article with all the author + an author who is not in the list
        article_list_expected = []
        for i in range(5):
            article = Article.objects.create()
            for author in author_list:
                Article_Author.objects.create(author=author,research=research)
            n = len(author_not_list)
            Article_Author.objects.create(author=author_not_list[random.randint(0,n-1)],research=research)
        
        # we create a number of article with some author not in the list and one author in the list
        article_list_not_expected = []
        for i in range(10):
            article = Article.objects.create()
            for i in range(random.randint(0,len(author_not_list))):
                Article_Author.objects.create(author=author_not_list[random.randint(0,len(author_not_list) - 1)],research=research)
            n = len(author_list)
            Article_Author.objects.create(author=author_list[random.randint(0,n-1)],research=research)
        
        # we create the output result
        output_result = get_Articles_Filtered(research,input)

        #we check if we have the good article and not bad article
        for article in article_list_expected:
            self.assertIn(article,output_result)
        for article in article_list_not_expected:
            self.assertNotIn(article,output_result)
        
    
    def test_neighbour(self):
        """we check if we have the 5 articles nearest from one article"""
        research = Research.objects.create()
        position_list = [(1,1),(2,2),(1,0),(3,3),(2,3)]

        position = (1.0,2.0)
        article_center = Article.objects.create(research=research,article=article,pos_x=1,pos_y=2,topic='')

        article_in_list = []
        for i in range(5):
            article = Article.objects.create()
            Cluster.objects.create(research=research,article=article,pos_x=position_list[i][0],pos_y=position_list[i][1],topic='')
            article_in_list.append(article)

        article_not_in_list = []
        for i in range(5):
            article = Article.objects.create()
            Cluster.objects.create(research=research,article=article,pos_x=20,pos_y=20,topic='')
            article_not_in_list.append(article)
        
        input = {"filter_0":{"author":[article_center]}}

        output_result= get_Articles_Filtered(research,input)

        #we check if the result is what we expect
        for article in article_in_list:
            self.assertIn(article,output_result)
        for article in article_not_in_list:
            self.assertNotIn(article,output_result)
        
    def test_keyword(self):
        pass