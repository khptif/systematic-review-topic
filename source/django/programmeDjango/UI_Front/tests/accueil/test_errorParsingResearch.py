from UI_Front.functions.accueil_functions import *
from django.test import TestCase

# Test of the function 'errorParsingResearch'
# the function check if the string give to the research form is correct

# input: string
# output: (boolean, string). (False,error message) if incorrect, (True,'') else

#(False,'Forbidden characters : {a list of forbidden characters}')
# input: a string with at most one character who is not 

class test_errorParsingResearch(TestCase):

    #(False,'Forbidden characters : {a list of forbidden characters}')
    # input: a string with at most one character who is not alphanumeric,'-', parenthesis, double quotes, ',' , ';', space,
    def test_forbidden_characters(self):

        function_to_test = errorParsingResearch

        # input with only forbidden characters
        input = """$!+<>"""
        output = (False, """Forbidden characters :  ' $ '  ' ! '  ' + '  ' < '  ' > ' """)
        out_assert = function_to_test(input)
        self.assertEqual(output,out_assert,"forbidden character test")

        # input with mix forbidden/ authorized characters
        input = """jgo!w-ho""gre(@grgro$+-grioqWEGS355323kog?"""
        output = (False, """Forbidden characters :  ' ! '  ' @ '  ' $ '  ' + '  ' ? ' """)
        out_assert = function_to_test(input)
        self.assertEqual(output,out_assert,"forbidden character test")
        