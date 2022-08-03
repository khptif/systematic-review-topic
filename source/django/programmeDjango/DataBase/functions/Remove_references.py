import re
#from booleansearchparser import BooleanSearchParser
import numpy as np

def remove_references(text):
    try:
        regex = re.compile(r"(^.+)(references|bibliography):?\s(.+)$", re.IGNORECASE | re.MULTILINE)
        stext = regex.sub(r"\1", text)
        regex = re.compile(r"(^.+)(acknowledgments|acknowledgment):?\s(.+)$", re.IGNORECASE | re.MULTILINE)
        stext = regex.sub(r"\1", stext)
        return (stext)
    except TypeError:
        return (text)

def check_searchterms(text, search_terms, default = True): #retruns true if there's a fail
    bsp = BooleanSearchParser()
    try:
        return bsp.match(text.lower(),search_terms.lower())
    except:
        return (default)
    #Returny True if the search expression works, False otherwise