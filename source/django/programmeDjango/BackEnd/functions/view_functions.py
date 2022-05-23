
from BackEnd.functions.Get_arXiV import get_article as arxiv,get_max_article as max_arxiv
from BackEnd.functions.Get_biorXiv import get_article as biorxiv, get_max_article as max_biorxiv
from BackEnd.functions.Get_medrXiv import get_article as medrxiv, get_max_article as max_medrxiv
from BackEnd.functions.Get_PAP import get_article as pap, get_max_article as max_pap

import BackEnd.functions.text_processing as text_processing
import BackEnd.functions.clustering as clustering

from DataBase.models import *
from BackEnd.models import *
from UI_Front.models import *

from threading import Thread
import time
import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from glob import glob

# remove stopwords and one and two characters words
list_stopwords = text_processing.create_stopwords()

from programmeDjango.settings import NUMBER_THREADS_ALLOWED
from programmeDjango.settings import NUMBER_TRIALS

def max_article(search):
    article = 0
    try:
        article += max_arxiv(search)
    except:
        pass
    try:
        article += max_biorxiv(search)
    except:
        pass
    try:
        article += max_medrxiv(search) 
    except:
        pass
    try:
        article += max_pap(search) 
    except:
        pass

    return  article

def make_research (search,research,thread=1):

    
    arg = (search,research,thread)
    thread_arxiv = Thread(target=arxiv,args=arg)
    thread_biorxiv = Thread(target=biorxiv,args=arg)
    thread_medrxiv = Thread(target=medrxiv,args=arg)
    thread_pap = Thread(target=pap,args=arg)

    thread_arxiv.start()
    thread_biorxiv.start()
    thread_medrxiv.start()
    thread_pap.start()

    thread_arxiv.join()
    thread_biorxiv.join()
    thread_medrxiv.join()
    thread_pap.join()


def preprocessing_parallel(research,articles,corpus):
    """ 
    The method get all the article from the research and preprocess the full text.
    The format of the articles list is a QuerySet
    We can choose which text we preprcesse. The abstract: "abstract, the full text: "full_text" or both : "both".
    It writes the result for each article in database in model "Preprocess_text"
    This method will be parallelized
    """
        
    #list of the text from the article
    #according the corpus argument, we define the list of text to be preprocessed
    text_list = []
    if corpus == "abstract":
        text_list = articles.values_list('abstract', flat=True)
    elif corpus == "full_text":
        text_list = articles.values_list('full_text', flat=True)
    elif corpus == "both":
        full_text = articles.values_list('full_text', flat=True)
        abstract = articles.values_list('abstract', flat=True)
        for i in range(articles.count()):
            text_list.append(str(abstract[i]) + str(full_text[i]))
    
    list_id = list(articles.values_list("id",flat=True))

    for i in range(len(list_id)):

        
        id_article = list_id[i]
        text = text_list[i]

        # we check if this articles was already preprocessed for this research
        if Preprocess_text.objects.filter(research = research, id_article=id_article).exists():
            continue

        # pre_processing
        list_pre_processing = text_processing.pre_processing([text])
        
        # define languages
        list_languages,id_list = text_processing.define_languages(list_pre_processing,[id_article])
        if len(list_languages) == 0:
            continue

        # sentences to words
        list_words = list(text_processing.sent_to_words(list_languages))

        # lemmatization keeping only noun, adj, vb, adv (only for english words)
        list_lemmatized = text_processing.lemmatization(list_words,allowed_postags=["NOUN", "ADJ", "VERB", "ADV"],)

        list_one_two = text_processing.remove_words(list_lemmatized, list_stopwords)

        # remove misspelled words (only for english words)
        list_misspelled = text_processing.remove_misspelled(list_one_two)

        # create bigrams and trigrams
        list_trigrams = text_processing.create_ngrams(list_misspelled)
        
        # we save each word in list of trigam and associate to the research and his article's id
        for word in list_trigrams[0]:
            Preprocess_text.objects.create(research=research,id_article=id_article,text=word)
        Number_preprocess.objects.create(research = research)

def make_preprocessing(research,corpus="abstract",number_thread=1):
    """ preprocessing of the articles of the research in parallel.
    the output is the tfidf results. We can use the abstract ="abstract" or the full_text="full_text" or the both = "both" """

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
    for articles in list_jobs:
        list_threads.append(Thread(target=preprocessing_parallel,args=(research,articles,corpus)))
        
    
    #We start the threads and wait for their ending
    for thread in list_threads:
        thread.start()
    for thread in list_threads:
        thread.join()
    

    #we recuperate the results from preprocessing
    preprocess = Preprocess_text.objects.filter(research=research)
    id_article_list = preprocess.values_list('id_article',flat=True).distinct().order_by()

    text_list = []
    for id_article in id_article_list:
        text_list.append(Preprocess_text.objects.filter(research=research,id_article=id_article).values_list("text",flat=True))
    
    # remove common words (>50% of articles) and unique words
    list_common_and_unique = text_processing.remove_common_and_unique(text_list)

    # remove empty abstracts after text processing
    list_id_final, list_final = text_processing.remove_empty(id_article_list, list_common_and_unique)
  
    # we build the list to build the tfidf
    list_tfidf =[]
    list_id_return = []
    for i in range(len(list_id_final)):
        if not list_id_final[i] == -1:
            list_tfidf.append(list_final[i])
            list_id_return.append(list_id_final[i])
    
    tfidfVectorizer = TfidfVectorizer()
    tf_idf = tfidfVectorizer.fit_transform(list_final)

    joblib.dump(list_final,f"BackEnd/data/final_list_research_{str(research.id)}.pkl")
    joblib.dump(tf_idf, f"BackEnd/data/tf_idf_research_{str(research.id)}.pkl")
    joblib.dump(list_id_final,f"BackEnd/data/id_list_research_{str(research.id)}.pkl")

    return tf_idf,list_id_return,list_final
    

def make_cluster(research,list_id,list_final,tf_idf,n_trials,n_threads):
    
    # run 2d pacmap with default values
    embedding_2d = clustering.pacmap_default(tf_idf)

    # run optimization
    study = clustering.optimization(
       research, tf_idf, "study_research_"+str(research.id), n_trials, n_threads
    )
    
    # extract best study
    best_study_clusterer = clustering.retrieve_best_study(
        tf_idf, study
    )
    
    # create hover matrix
    clustering.hover_with_keywords(
        research,
        list_id,
        list_final,
        embedding_2d,
        best_study_clusterer
    )

def back_process(research):
    """ when a research request is done, this method is launched. If there is a fault and this method is restarted,
        we have to continue to the point where it was stopped. When everything is finish, the method have to clear all 
        non necessery data"""
    tf_idf =[]
    id_list = []
    final_list = []

    research.is_running = True
    research.save()
    #we check in which step is the research
    if research.step == "article":

        search = research.search
        # we give the max article possible to get so we can see the progression
        research.max_article = max_article(search)
        make_research(search,research,NUMBER_THREADS_ALLOWED)
        # when it's done, we change the current step
        research.step = "processing"
        research.save()

    if research.step == "processing":
        tf_idf,id_list,final_list = make_preprocessing(research=research,corpus="abstract",number_thread=NUMBER_THREADS_ALLOWED)
        research.step = "clustering"
        research.save()

    if research.step == "clustering":
        # if the tf_idf and other data are null, we charge them from save files
        if tf_idf == []:
            tf_idf = joblib.load(f"BackEnd/data/tf_idf_research_{str(research.id)}.pkl")
        if id_list == []:
            id_list = joblib.load(f"BackEnd/data/id_list_research_{str(research.id)}.pkl")
        if final_list == []:
            final_list = joblib.load(f"BackEnd/data/final_list_research_{str(research.id)}.pkl")
    
        make_cluster(research,id_list,final_list,tf_idf,NUMBER_TRIALS,NUMBER_THREADS_ALLOWED)
        # we reset the step to "article" and mark the research as "finished"
        research.is_running = False
        research.is_finish = True
        research.step = "article"
        research.save()

        # clear all useless data
        if os.path.exists(f"BackEnd/data/tf_idf_research_{str(research.id)}.pkl"):
            os.remove(f"BackEnd/data/tf_idf_research_{str(research.id)}.pkl")
        if os.path.exists(f"BackEnd/data/id_list_research_{str(research.id)}.pkl"):
            os.remove(f"BackEnd/data/id_list_research_{str(research.id)}.pkl")
        if os.path.exists(f"BackEnd/data/final_list_research_{str(research.id)}.pkl"):
            os.remove(f"BackEnd/data/final_list_research_{str(research.id)}.pkl")

        Preprocess_text.objects.filter(research=research).delete()
        Number_preprocess.objects.filter(research=research).delete()
        PID_Research.objects.filter(research=research).delete()
        Number_preprocess.objects.filter(research = research).delete()

def relaunch_backprocess(research):
    """we define this method to run the method in another process and return with the child process.
        The goal is to not have the method running in a child process created by fork(). Otherwise,
        the package optuna who use OpenMP get error."""
    from django import db
    db.connections.close_all()
    #we fork
    pid = os.fork()
    #parent process return httpresponse
    if pid > 0:
        pid = os.getpid()
        old_pid = PID_Research.objects.filter(research=research).delete()
        PID_Research.objects.create(research=research,pid=pid)
        back_process(research)
    # child process
    elif pid == 0:
        return True
    else:
        return False

def relaunch_if_fault():
    """This is a infiny loop who check if there is a research who is running but there is no more process with his associated pid"""

    while True:
        research_list = Research.objects.filter(is_running = True)

        for research in research_list:
            pid = PID_Research.objects.filter(research=research)
            try:
                pid = pid[0].pid
                os.kill(pid, 0)
                time.sleep(5)
            except OSError:
                # the process doesn't exists anymore so we restart it
                relaunch_backprocess(research)
            
            
def update_research():
    """This is a infinity loop who every 1 month, restart all research who is finished. But, between each restart, we give some time
    so the host doesn't freeze"""
    while True:
        from programmeDjango.settings import UPDATE_INTERVAL
        time.sleep(UPDATE_INTERVAL)
        research_list = Research.objects.filter(is_finish = True)
        for research in research_list:
            relaunch_backprocess(research)
            time.sleep(3600)