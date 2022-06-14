
from django.test import TestCase
from UI_Front.functions.select_functions import *


class test_filters_manager(TestCase):
    """ We separatly test each type of value between 'topic','author','keyword' and 'neighbour'.
        And the last test is with all of them together"""

    def test_topic_value(self):
        """ We test with two input for test the topic entry. One who is correct and the other incorrect.
            We test too if the the name topic is good"""
        
        topic = "qwertQWERT, qw-ew12 , lpogkLPF_123XCS"
        input_correct = {"filter_0_1" : "Type:topic;topic_name:{topic}".format(topic=topic)}
        input_incorrect = {"flter_0_1" : "Type:topic;topic_name:{topic}".format(topic=topic)}

        output_correct_expected = {"filter_0" : {"topic":[topic]}}
        output_incorrect_expected = {}

        output_correct_result = filters_manager(False,input_correct)
        output_incorrect_result = filters_manager(False,input_incorrect)

        self.assertEqual(output_correct_expected,output_correct_result)
        self.assertEqual(output_incorrect_expected,output_incorrect_result)

    def test_author(self):
        """ we give three authors. The two first have the same last name and the two last have the same first name.
            We test with names of the second author.
            We make 3 test: last name,first name and a name that didn't appear """

        #mock authors
        author1 = Author.objects.create(last_name ="Lefebvre",first_name="Antoine")
        author2 = Author.objects.create(last_name ="Lefebvre",first_name="Pierre")
        author3 = Author.objects.create(last_name ="Ratier",first_name="Pierre")

        #inputs
        input1 = {"filter_0_1" : "Type:author;name:Lefebvre;"}
        input2 = {"filter_0_1" : "Type:author;name:Pierre;"}
        input3 = {"filter_0_1" : "Type:author;name:Jean;"}

        #expected output
        output1_expected = [author1,author2]
        output2_expected = [author2,author3]
        output3_expected = {}

        #result output
        output1_result = filters_manager(False,input1)['filter_0']['author']
        output2_result = filters_manager(False,input2)['filter_0']['author']
        output3_result = filters_manager(False,input3)['filter_0']

        for a in output1_expected:
            self.assertIn(a,output1_result)
        for a in output2_expected:
            self.assertIn(a,output2_result)
        
        self.assertEqual(output3_expected,output3_result)

    def test_keyword(self):
        """ we give three keywords and check if result is correct"""
        keyword1="TesT1_"
        keyword2="tE-St2_"
        keyword3="TE ST 3"

        input = {   "filter_0_1": "Type:keyword;keyword:{key};".format(key=keyword1),
                    "filter_0_2": "Type:keyword;keyword:{key};".format(key=keyword2),
                    "filter_0_3": "Type:keyword;keyword:{key};".format(key=keyword3)}
        
        output_expected = {"filter_0":{"keyword":[keyword1,keyword2,keyword3]}}
        output_result = filters_manager(False,input)

        self.assertEqual(output_result,output_expected)

    def test_neighbour(self):
        """ we create an article with the doi and check if we obtain this article"""
        doi = "1234./32kfow._425-greqkog/10.110140"

        article = Article.objects.create(doi=doi)
        research = Research.objects.create()
        Research_Article.objects.create(article=article,research=research)

        input = {"filter_0_1": "Type:neighbour;DOI:{doi};".format(doi=doi)}
        output_expected = {"filter_0":{"neighbour":[article]}}
        output_result = filters_manager(research,input)
    
        self.assertEqual(output_expected,output_result)

    def test_alltogether(self):
        topic="topic_test"

        last_name="test1"
        first_name="test2"
        author=Author.objects.create(last_name=last_name,first_name=first_name)

        keyword = "key_test"

        doi = "1234"
        article = Article.objects.create(doi=doi)
        research = Research.objects.create()
        Research_Article.objects.create(article=article,research=research)

        input = {   "filter_0_1":"Type:topic;topic_name:{topic}".format(topic=topic),
                    "filter_0_2":"Type:author;name:{name};".format(name=last_name),
                    "filter_0_3":"Type:keyword;keyword:{key};".format(key=keyword),
                    "filter_0_4":"Type:neighbour;DOI:{doi};".format(doi=doi)}

        output_expected = {"filter_0" : {"topic":[topic],"author":[author],"keyword":[keyword],"neighbour":[article]}}
        output_result = filters_manager(research,input)
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
        research = Research.objects.create()
        Research_Article.objects.create(article=article,research=research)

        input = {   "filter_0_1":"Type:topic;topic_name:{topic}".format(topic=topic),
                    "filter_0_2":"Type:author;name:{name};".format(name=last_name),
                    "filter_0_3":"Type:keyword;keyword:{key};".format(key=keyword),
                    "filter_0_4":"Type:neighbour;DOI:{doi};".format(doi=doi),

                    "filter_1_1":"Type:topic;topic_name:{topic}".format(topic=topic),
                    "filter_1_2":"Type:author;last_name:{name};".format(name=first_name),
                    "filter_1_3":"Type:keyword;keyword:{key};".format(key=keyword),
                    "filter_1_4":"Type:neighbour;DOI:{doi};".format(doi=doi) }

        output_expected = { "filter_0" : {"topic":[topic],"author":[author],"keyword":[keyword],"neighbour":[article]},
                            "filter_1" : {"topic":[topic],"author":[author],"keyword":[keyword],"neighbour":[article]}}
        output_result = filters_manager(research,input)

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
        #we create the cluster for other topic randomly
        import random
        n_other_topic = len(topic_other)
        for article in article_not_in_topic:
            Cluster.objects.create(article=article,pos_x=0,pos_y=0,topic=topic_other[random.randint(0,n_other_topic-1)],research=research)
        
        # we define input
        input = {"filter_0":{"topic":[topic]}}
        # we get the results
        output_result = get_Articles_Filtered(research,input)

        #we check if we have the good article

        for article in article_in_topic:
            self.assertIn(article.id,output_result)

        for article in article_not_in_topic:
            self.assertNotIn(article.id,output_result)
        
    def test_author(self):
        """We test if get the article written by the right authors. the article match if it was written by all authors in list atmost"""
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
            # we create the article expected
            article = Article.objects.create()
            article_list_expected.append(article) 
            # we give all good author to the article
            for author in author_list:
                Article_Author.objects.create(author=author,article=article)
            # we give one of the bad author to the article
            n = len(author_not_list)
            Article_Author.objects.create(author=author_not_list[random.randint(0,n-1)],article=article)
            # we add the article to the research
            Research_Article.objects.create(research=research,article=article)
        
        # we create a number of article with some author not in the list and one author in the list
        article_list_not_expected = []
        for i in range(10):
            #we create the article not expected
            article = Article.objects.create()
            article_list_not_expected.append(article)
            # we give a number of bad author to the article
            for i in range(random.randint(0,len(author_not_list))):
                Article_Author.objects.create(author=author_not_list[random.randint(0,len(author_not_list) - 1)],article=article)
            # we give one good author to the article
            n = len(author_list)
            Article_Author.objects.create(author=author_list[random.randint(0,n-1)],article=article)
            Research_Article.objects.create(research=research,article=article)
        
        # we create the output result
        output_result = get_Articles_Filtered(research,input)

        #we check if we have the good article and not bad article

        for article in article_list_expected:
            self.assertIn(article.id,output_result)

        for article in article_list_not_expected:
            self.assertNotIn(article.id,output_result)
        
    
    def test_neighbour(self):
        """we check if we have the nearest articles from one article"""
        import random

        number_neighbour = 5
        center_position = (5,5)
        research = Research.objects.create()

        # define the nearest et farest position
        near_position_list = []
        for i in range(number_neighbour):
            x = center_position[0] + random.randint(-2,2)
            y = center_position[1] + random.randint(-2,2)
            near_position_list.append((x,y))
        
        far_position_list = []
        for i in range(random.randint(10,50)):
            x = center_position[0] + random.randint(-20,20) + 100
            y = center_position[1] + random.randint(-20,20) + 100
            far_position_list.append((x,y))

        # we create the article in center
        article_center = Article.objects.create(research=research,pos_x=center_position[0],pos_y=center_position[1],topic='')

        # we create other article with their Cluster object
        near_article_list = []
        for x,y in near_position_list:
            article = Article.objects.create()
            Cluster.objects.create(research=research,article=article,pos_x=x,pos_y=y,topic='')
            near_article_list.append(article)
            Research_Article(research=research,article=article)

        far_article_list = []
        for x,y in far_position_list:
            article = Article.objects.create()
            Cluster.objects.create(research=research,article=article,pos_x=x,pos_y=y,topic='')
            far_article_list.append(article)
            Research_Article(research=research,article=article)
        
        input = {"filter_0":{"author":[article_center]}}

        output_result= get_Articles_Filtered(research,input)

        #we check if the result is what we expect
        for article in near_article_list:
            self.assertIn(article.id,output_result)
        for article in far_article_list:
            self.assertNotIn(article.id,output_result)
        
    def test_keyword(self):
        pass