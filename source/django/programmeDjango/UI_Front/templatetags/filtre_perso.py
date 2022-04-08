
from django import template
from django.conf import settings

import html

from DataBase.models import *

register = template.Library()

@register.filter
def get_first_param(elem):
    return elem[0]

@register.filter
def historical(research):
    """ 
    A research is in the format : (id_research, [list of key_words who match the search]).for each research, we give the line 
    string chain, keywords(the one who match in bold), number of articles
    """
    return_string = ""
    research_object = Research.objects.get(id=research[0])
    all_keywords = Keyword.objects.filter(research=research_object).order_by('word')

    # string search
    return_string += "[ " + html.escape(research_object.search) + "] | "
    # keywords
    for key in all_keywords:
        if key.word in research[1]:
            return_string += "<b>" + html.escape(key.word) + "</b>, "
        else:
            return_string += html.escape(key.word) + ", "
    return_string += " | "
    # number of articles
    number_article = len(Research_Article.objects.filter(research=research_object))
    return_string += str(number_article) + " articles | "

    return return_string