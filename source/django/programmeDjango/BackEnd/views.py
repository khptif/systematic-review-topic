from datetime import date
from django.shortcuts import render
from BackEnd.functions.Get_arXiV import get_article as arxiv,get_max_article as max_arxiv
from BackEnd.functions.Get_biorXiv import get_article as biorxiv, get_max_article as max_biorxiv
from BackEnd.functions.Get_medrXiv import get_article as medrxiv, get_max_article as max_medrxiv
from BackEnd.functions.Get_PAP import get_article as pap, get_max_article as max_pap

import BackEnd.functions.text_processing as text_processing

from DataBase.models import *
from threading import Thread
import time


# Create your views here.

def research (search,research,thread=1):

    total = max_arxiv(search) + max_biorxiv(search) + max_medrxiv(search) + max_pap(search)
    print("Total article: " + str(total))

    arg = (search,research,thread)
    thread_arxiv = Thread(target=arxiv,args=arg)
    thread_biorxiv = Thread(target=biorxiv,args=arg)
    thread_medrxiv = Thread(target=medrxiv,args=arg)
    thread_pap = Thread(target=pap,args=arg)

    thread_arxiv.start()
    thread_biorxiv.start()
    thread_medrxiv.start()
    thread_pap.start()

    temps = 0
    max_time = 500
    now = datetime.datetime.now()
    while temps < max_time :
        time.sleep(2)
        article_total = Research_Article.objects.filter(research=research).count()
        print("Total article: " + str(article_total) + " on " + str(total))

        temps = datetime.datetime.now() - now
        temps = temps.seconds
    thread_arxiv.join()
    thread_biorxiv.join()
    thread_medrxiv.join()
    thread_pap.join()


def preprocessing(research):
    """ 
    The method get all the article from the research and preprocess the full text.
    The output is a file with the tf-idf
    """
        
    #list of the full_text from the article
    articles = Article.objects.filter(research_article__research = research).order_by('id')
    full_text_list = articles.values_list('full_text', flat=True)
    id_list = articles.values_list("id",flat=True)

    print("prepoc")
    # pre_processing
    list_pre_processing = text_processing.pre_processing(full_text_list)

    print('define language')
    # define languages
    list_languages = text_processing.define_languages(list_pre_processing)

    # sentences to words
    list_words = list(text_processing.sent_to_words(list_languages))

    print('lemmatization')
    # lemmatization keeping only noun, adj, vb, adv (only for english words)
    list_lemmatized = text_processing.lemmatization(list_words,allowed_postags=["NOUN", "ADJ", "VERB", "ADV"],)

    # remove stopwords and one and two characters words
    list_stopwords = text_processing.create_stopwords()

    list_one_two = text_processing.remove_words(list_lemmatized, list_stopwords)

    # remove misspelled words (only for english words)
    list_misspelled = text_processing.remove_misspelled(list_one_two)

    # create bigrams and trigrams
    list_trigrams = text_processing.create_ngrams(list_misspelled)

    # remove common words (>50% of articles) and unique words
    list_common_and_unique = text_processing.remove_common_and_unique(list_trigrams)

    # remove empty abstracts after text processing
    list_id_final, list_final = text_processing.remove_empty(id_list, list_common_and_unique)


