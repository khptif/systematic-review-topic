from django.test import TestCase
from BackEnd.functions.text_processing import *

class test_pre_processing(TestCase):
    # this method remove some element from the text.
    # For each element, we will test with a text.
    # The last will be a test with all element to remove in the same text

    def test_remove_emails(self):
        input = "This is an example@email.com for test"
        output_expected = "This is an for test"
        output_result = pre_processing([input])[0]

        self.assertEqual(output_expected,output_result)
    
    def test_remove_new_line(self):
        input = "This is an newline \n for test"
        output_expected = "This is an newline for test"
        output_result = pre_processing([input])[0]

        self.assertEqual(output_expected,output_result)

    def test_remove_single_quotes(self):
        input = "This is an 'example' for test"
        output_expected = "This is an example for test"
        output_result = pre_processing([input])[0]

        self.assertEqual(output_expected,output_result)

    def test_remove_http(self):
        input = "http://url.adresse.com for test"
        output_expected = "for test"
        output_result = pre_processing([input])[0]

        self.assertEqual(output_expected,output_result)

    def test_remove_www(self):
        input = "This is an www.adresse.web.com for test"
        output_expected = "This is an  for test"
        output_result = pre_processing([input])[0]

        self.assertEqual(output_expected,output_result)

    def test_remove_all(self):
        input = "This is an example@email.com \n 'example' https://url.adresse.com www.adresse.web.com for test"
        output_expected = "This is an      for test"
        output_result = pre_processing([input])[0]

        self.assertEqual(output_expected,output_result)

class test_define_language(TestCase):
    # we check if the language is english in text.
    # we will check only for two text: one in English and one in French.

    def test_english(self):
        input = "This is an english text"
        output_expected = (["This is an english text"],[1])
        output_result = define_languages([input],[1])

        self.assertEqual(output_expected,output_result)

    def test_french(self):
        input = "Ceci est un texte en français"
        output_expected = ([""],[-1])
        output_result = define_languages([input],[1])

        self.assertEqual(output_expected,output_result)

