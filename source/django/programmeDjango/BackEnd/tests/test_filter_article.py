from django.test import TestCase
from BackEnd.functions.filter_article import *

class test_split_search_term(TestCase):

    #Test of the function "parse_search_term(search).
    #
    #input:     string that represents the complete reserching
    #output:    list of each element of splitted , 
    #           dictinnary where each key is keyword from string research and value is a empty list
    #
    #Don't check for forbidden element

    def test_simple_word(self):
        """ string research is constitued from one key words.
            We check for single keywords """

        function_to_test = split_search_term
        
        input_test = ["word","(word)"]
        output_test = [function_to_test(i) for i in input_test]
        excepted_output = [( ["word"] , {"word":[] } ),(['(','word',')'], {"word":[]})]

        #we check value
        number = 0
        for i in range(len(excepted_output)):
            print("check :"+ input_test[i])
            self.assertEqual(excepted_output[i],output_test[i],"problem input: "+ input_test[i])
            print("Ok!")
    
    def test_logical_op(self):
        """ we check for research string that contains OR and AND logical operation"""
        pass




class test_parsing(TestCase):

    def test_one_keyword(self):
        
        function_to_test = parsing

        input_test = ( ["word"] , {"word":[1,2,3,4] } )
        out_put = function_to_test(input_test[0],input_test[1])

        except_output = [1,2,3,4]

        self.assertEqual(except_output, out_put)