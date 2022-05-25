from django.test import TestCase
from UI_Front.functions.select_functions import *


class test_filters_manager(TestCase):

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

    