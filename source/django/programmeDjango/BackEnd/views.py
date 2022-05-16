from concurrent.futures import thread
from datetime import date
from django.shortcuts import render
from BackEnd.functions.Get_arXiV import get_article as arxiv,get_max_article as max_arxiv
from BackEnd.functions.Get_biorXiv import get_article as biorxiv, get_max_article as max_biorxiv
from BackEnd.functions.Get_medrXiv import get_article as medrxiv, get_max_article as max_medrxiv
from BackEnd.functions.Get_PAP import get_article as pap, get_max_article as max_pap

import BackEnd.functions.text_processing as text_processing

from DataBase.models import *
from BackEnd.models import *
from threading import Thread
import time

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

# remove stopwords and one and two characters words
list_stopwords = text_processing.create_stopwords()

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


def preprocessing_parallel(research,articles,numero):
    """ 
    The method get all the article from the research and preprocess the full text.
    The format of the articles list is a QuerySet
    It writes the result for each article in database in model "Preprocess_text"
    This method will be parallelized
    """
        
    #list of the full_text from the article
    full_text_list = articles.values_list('full_text', flat=True)
    list_id = list(articles.values_list("id",flat=True))

    for i in range(len(list_id)):

        print("\rarticle "+str(i)+" / "+str(len(list_id)) + " numero: " + str(numero)) 

        id_article = list_id[i]
        full_text = full_text_list[i]

        # we check if this articles was already preprocessed for this research
        if Preprocess_text.objects.filter(research = research, id_article=id_article).exists():
            continue


        # pre_processing
        list_pre_processing = text_processing.pre_processing([full_text])
        
        # define languages
        list_languages,id_list = text_processing.define_languages(list_pre_processing,[id_article])

        # sentences to words
        list_words = list(text_processing.sent_to_words(list_languages))

        # lemmatization keeping only noun, adj, vb, adv (only for english words)
        list_lemmatized = text_processing.lemmatization(list_words,allowed_postags=["NOUN", "ADJ", "VERB", "ADV"],)

        list_one_two = text_processing.remove_words(list_lemmatized, list_stopwords)

        # remove misspelled words (only for english words)
        list_misspelled = text_processing.remove_misspelled(list_one_two)

        # create bigrams and trigrams
        list_trigrams = text_processing.create_ngrams(list_misspelled)

        # remove common words (>50% of articles) and unique words
        list_common_and_unique = text_processing.remove_common_and_unique(list_trigrams)

        # remove empty abstracts after text processing
        list_id_final, list_final = text_processing.remove_empty([id_article], list_common_and_unique)

        if list_id_final[0] == -1:
            Preprocess_text.objects.create(research=research,id_article=id_article,text="")
            continue
        
        Preprocess_text.objects.create(research=research,id_article=id_article,text=list_final[0])

def preprocessing(research,number_thread=1):
    """ preprocessing of the articles of the research in parallel.
    the output is the tfidf results"""

    #we get the articles
    articles = Article.objects.filter(research_article__research=research)

    #we will ditribute the jobs among the threads
    # the input is a list of article
    list_jobs = []
    number_article = articles.count()
    number_job_by_thread = int(number_article / number_thread)
    
    for i in range(number_thread):
        list_jobs.append(articles[i*number_job_by_thread : (i+1)*number_job_by_thread])
    # the last jobs are given to the last thread. So there are one more thread.
    list_jobs.append(articles[number_thread*number_job_by_thread :])

    #We create the threads
    list_threads = []
    i=1
    for articles in list_jobs:

        list_threads.append(Thread(target=preprocessing_parallel,args=(research,articles,i)))
        i +=1
    
    #We start the threads and wait for their ending
    for thread in list_threads:
        thread.start()
    for thread in list_threads:
        thread.join()
    
    #we recuperate the results from preprocessing
    preprocess = Preprocess_text.objects.filter(research=research).exclude(text="").order_by("id_article")
    text_list = preprocess.values_list('text', flat=True)
    id_list = preprocess.values_list('id_article',flat=True)
    
    tfidfVectorizer = TfidfVectorizer()
    tf_idf = tfidfVectorizer.fit_transform(text_list)

    joblib.dump(tf_idf, f"BackEnd/data/tf_idf_research_{str(research.id)}.pkl")
    joblib.dump(id_list,f"BackEnd/data/id_list_research_{str(research.id)}.pkl")

    return tf_idf,id_list
    

