
from BackEnd.functions.Get_arXiV import get_article as arxiv,get_max_article as max_arxiv
from BackEnd.functions.Get_biorXiv import get_article as biorxiv, get_max_article as max_biorxiv
from BackEnd.functions.Get_medrXiv import get_article as medrxiv, get_max_article as max_medrxiv
from BackEnd.functions.Get_PAP import get_article as pap, get_max_article as max_pap
from BackEnd.functions.Get_PMC import get_article as pmc, get_max_article as max_pmc
from BackEnd.functions.Get_PM import get_article as pm, get_max_article as max_pm
from BackEnd.functions.scatter_with_hover import scatter_with_hover

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
from programmeDjango.settings import TEMPORARY_DATA,PLOT_DATA

# all research processing will be done in a new thread. We keep the thread object
# to check if it is still alive
# the key is the research id and the value is the thread object
list_thread = dict()

# we redirect stderror to a file
import sys
#sys.stderr = open(TEMPORARY_DATA + "/error.log","a")

def print_research(output_text,research_id):
    """ we print in the file log of the research"""
    a = open(TEMPORARY_DATA + "/research_" + str(research_id) + ".log","a")
    try:
        print(output_text,file=a)
    finally:
        a.close()


def max_article(search,begin,end):
    article = 0
    try:
        article += max_arxiv(search)
    except:
        print("error arxiv",file=sys.stderr)
        pass

    try:
        article += max_biorxiv(search,begin,end)
    except:
        print("error bio",file=sys.stderr)
        pass
     
    try:
        article += max_medrxiv(search,begin,end) 
    except:
        print("error med",file=sys.stderr)
        pass

    try:
        article += max_pap(search,begin,end) 
    except:
        print("error pap",file=sys.stderr)
        pass
    
    try:
        article += max_pmc(search,begin,end) 
    except:
        print("error pmc",file=sys.stderr)
        pass

    try:
        article += max_pm(search,begin,end) 
    except:
        print("error pubmed",file=sys.stderr)
        pass

    return  article

def make_research (search,research,begin,end,thread=1):

    arg = (search,research,begin,end,thread)
    
    print_research("Research thread created",research.id)

    if research.current_article_db == '':
        research.current_article_db = "arxiv"
        research.save()
        step_article = Article_Step.objects.create(research=research,step="")
    else:
        step_article = Article_Step.objects.get(research=research)
    
    if research.current_article_db == "arxiv":
    
        thread_arxiv = Thread(target=arxiv,args=arg)
        thread_arxiv.start()
        print_research("Research in arxiv begin",research.id)
        thread_arxiv.join()
        print_research("Research in arxiv end",research.id)
        step_article.step = ""
        step_article.save()
        Article_Job.objects.filter(research = research).delete()
        research.current_article_db = "biorxiv"
        research.save()

    
    if research.current_article_db == "biorxiv":

        thread_biorxiv = Thread(target=biorxiv,args=arg)
        thread_biorxiv.start()
        print_research("Research in biorxiv begin",research.id)
        thread_biorxiv.join()
        print_research("Research in biorxiv end",research.id)
        step_article.step = ""
        step_article.save()
        Article_Job.objects.filter(research = research).delete()
        research.current_article_db = "medrxiv"
        research.save()

    if research.current_article_db == "medrxiv":

        thread_medrxiv = Thread(target=medrxiv,args=arg)
        thread_medrxiv.start()
        print_research("Research in medrxiv begin",research.id)
        thread_medrxiv.join()
        print_research("Research in medrxiv end",research.id)
        step_article.step = ""
        step_article.save()
        Article_Job.objects.filter(research = research).delete()
        research.current_article_db = "paperity"
        research.save()

    if research.current_article_db == "paperity":

        thread_pap = Thread(target=pap,args=arg)
        thread_pap.start()
        print_research("Research in paperity begin",research.id)
        thread_pap.join()
        print_research("Research in paperity end",research.id)
        step_article.step = ""
        step_article.save()
        research.current_article_db = "PMC"
        research.save()

    if research.current_article_db == "PMC":

        thread_pmc = Thread(target=pmc,args=arg)
        thread_pmc.start()
        print_research("Research in pmc begin",research.id)
        thread_pmc.join()
        print_research("Research in pmc end",research.id)
        step_article.step = ""
        step_article.save()
        research.current_article_db = "PM"
        research.save()

    if research.current_article_db == "PM":
        
        thread_pm = Thread(target=pm,args=arg)
        thread_pm.start()
        print_research("Research in pm begin",research.id)
        thread_pm.join()
        print_research("Research in pm end",research.id)
        step_article.step = ""
        step_article.save()
        research.current_article_db = ""
        research.save()


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
            Number_preprocess.objects.create(research=research)
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


    #we clear the ancient number of preprocess article
    Number_preprocess.objects.filter(research=research).delete()

    print_research("Number_preprocess objects cleaned",research.id)

    #we get the articles
    articles = Article.objects.filter(research_article__research=research)
    print_research("Articles fetched",research.id)

    print_research("Distribution of the article to each thread",research.id)
    #we will distribute the jobs among the threads
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
        
    print_research("Starting the threads",research.id)
    #We start the threads and wait for their ending
    for thread in list_threads:
        thread.start()
        print_research("Thread " + " started",research.id)
    
    for thread in list_threads:
        thread.join()
        print_research("Thread " + " ended",research.id)
    

    print_research("Building tf-idf file",research.id)
    #we recuperate the results from preprocessing
    preprocess = Preprocess_text.objects.filter(research=research)
    id_article_list_query_set = preprocess.values_list('id_article',flat=True).distinct().order_by()
    # we need change some value of id_list but QuerySet object doesn't allow assignment value.
    # we change from queryset to a usual list
    id_article_list = []
    for id in id_article_list_query_set:
        id_article_list.append(id)

    text_list = []
    for id_article in id_article_list:
        text_list.append(Preprocess_text.objects.filter(research=research,id_article=id_article).values_list("text",flat=True))
    
    # remove common words (>50% of articles) and unique words
    list_common_and_unique = text_processing.remove_common_and_unique(text_list)

    # remove empty abstracts after text processing
    list_id_final, list_final = text_processing.remove_empty(id_article_list, list_common_and_unique)
  
    # we build the tfidf
    tfidfVectorizer = TfidfVectorizer()
    tf_idf = tfidfVectorizer.fit_transform(list_final)

    print_research("Save temporary file",research.id)
    joblib.dump(list_final,f"{TEMPORARY_DATA}/final_list_research_{str(research.id)}.pkl")
    joblib.dump(tf_idf, f"{TEMPORARY_DATA}/tf_idf_research_{str(research.id)}.pkl")
    joblib.dump(list_id_final,f"{TEMPORARY_DATA}/id_list_research_{str(research.id)}.pkl")

    return tf_idf,list_id_final,list_final
    

def make_cluster(research,list_id,list_final,tf_idf,n_trials,n_threads):
    
    #we check the number of trial already accomplished and give only the unaccomplished number of trials
    trials_finished = Number_trial.objects.filter(research=research).count()
    n_trials = n_trials - trials_finished
    if n_trials <= 0:
        n_trials = 0

    print_research("2d pacmap run " ,research.id)
    # run 2d pacmap with default values
    embedding_2d = clustering.pacmap_default(tf_idf)

    print_research("Optimization begin" ,research.id)
    # run optimization
    study = clustering.optimization(
       research, tf_idf, "study_research_"+str(research.id), n_trials, n_threads
    )
    print_research("Optimization end" ,research.id)
    # extract best study
    best_study_clusterer = clustering.retrieve_best_study(
        research,tf_idf, study
    )
    
    print_research("writing cluster dat in database",research.id)
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

    time_start = datetime.datetime.now()
    research.is_running = True
    research.begining_date = time_start.date()
    research.save()

    begin_date = research.year_begin
    end_date = research.year_end

    print_research("\n\n ################ RESEARCH BEGINNING ################# \nsearch_terme = " + research.search + "\n",research.id)

    if research.step == "article":

        print_research("Article Step begin",research.id)
        search = research.search
        print_research("Article research start",research.id)
        make_research(search,research,begin_date,end_date,NUMBER_THREADS_ALLOWED)
        print_research("Article research done",research.id)
        # when it's done, we change the current step
        research.step = "processing"
        research.save()
        print_research("Article Step end",research.id)

    if research.step == "processing":
        print_research("Preprocessing Step begin",research.id)
        print_research("Preprocessing article begin",research.id)
        tf_idf,id_list,final_list = make_preprocessing(research=research,corpus="abstract",number_thread=NUMBER_THREADS_ALLOWED)
        print_research("Preprocessin article end",research.id)
        research.step = "clustering"
        research.save()
        print_research("Article Step end",research.id)

    if research.step == "clustering":
        print_research("Clustering Step begin",research.id)
        print_research("Recuperate temporary file if don't exist",research.id)
        # if the tf_idf and other data are null, we charge them from save files
        if tf_idf == []:
            tf_idf = joblib.load(f"{TEMPORARY_DATA}/tf_idf_research_{str(research.id)}.pkl")
        if id_list == []:
            id_list = joblib.load(f"{TEMPORARY_DATA}/id_list_research_{str(research.id)}.pkl")
        if final_list == []:
            final_list = joblib.load(f"{TEMPORARY_DATA}/final_list_research_{str(research.id)}.pkl")

        print_research("Clusterin begin",research.id)
        make_cluster(research,id_list,final_list,tf_idf,NUMBER_TRIALS,NUMBER_THREADS_ALLOWED)
        print_research("Clusterin end",research.id)
        
        # we create the plot html of clusters
        from programmeDjango.settings import is_decentralized
        if is_decentralized:
            from remote_functions import create_plot_remote
            create_plot_remote(research)
        else:
            scatter_with_hover(research, PLOT_DATA + "/research_{id}_plot.html".format(id=research.id))

        # we reset the step to "article" and mark the research as "finished"
        research.is_running = False
        research.is_finish = True
        research.step = "article"
        research.save()

        print_research("Delete temporary file",research.id)
        # clear all useless data
        if os.path.exists(f"{TEMPORARY_DATA}/tf_idf_research_{str(research.id)}.pkl"):
            os.remove(f"{TEMPORARY_DATA}/tf_idf_research_{str(research.id)}.pkl")
        if os.path.exists(f"{TEMPORARY_DATA}/id_list_research_{str(research.id)}.pkl"):
            os.remove(f"{TEMPORARY_DATA}/id_list_research_{str(research.id)}.pkl")
        if os.path.exists(f"{TEMPORARY_DATA}/final_list_research_{str(research.id)}.pkl"):
            os.remove(f"{TEMPORARY_DATA}/final_list_research_{str(research.id)}.pkl")

        Preprocess_text.objects.filter(research=research).delete()
        Number_preprocess.objects.filter(research=research).delete()
        Number_trial.objects.filter(research=research).delete()
        print_research("Clustering Step end",research.id)
        

    time_end = datetime.datetime.now()
    numbers_seconds = (time_end - time_start).seconds
    research.process_time = numbers_seconds
    research.save()

    print_research("\n\n ################ RESEARCH END ################# \n\n",research.id)
    del list_thread[research.id]

def launch_process(research):
    #we check if the research was already done
    if research.is_finish:
        return False

    #we check if the research is currently running
    if research.is_running:
        return False

    research_id = research.id
    list_thread[research_id] = Thread(target=back_process,args=[research])
    list_thread[research_id].setDaemon(True)
    list_thread[research_id].start()

    return True
    

def relaunch_if_fault():
    """ check if there is a research who is running but there is no more thread alive."""

   
    research_list = Research.objects.filter(is_running = True)

    for research in research_list:

        #we check if the research has his own entry
        if not research.id in list_thread:
            list_thread[research.id] = Thread(target=back_process,args=[research])
            list_thread[research.id].setDaemon(True)
            list_thread[research.id].start()
            continue

        t = list_thread[research.id]
        if not t.is_alive():
            # if the thread is not alive, we check if the the research is already finished
            r = Research.objects.filter(id=research.id)
            # if the research exist no more, it means it was deleted and it's ok that the thread is not running
            # and we pass to next iteration
            if not r.exists():
                continue
            else:
                r = r[0]
                if r.is_running:
                    #if the research is_running is true, we recreate a new thread
                    list_thread[research.id] = Thread(target=back_process,args=[research])
                    list_thread[research.id].setDaemon(True)
                    list_thread[research.id].start()
                else:
                    continue
            
            
def update_research():
    """This is a infinity loop who every 1 month, restart all research who is finished. But, between each restart, we give some time
    so the host doesn't freeze"""
    while True:
        from programmeDjango.settings import UPDATE_INTERVAL
        time.sleep(UPDATE_INTERVAL)
        research_list = Research.objects.filter(is_finish = True)
        for research in research_list:
            list_thread[research.id] = Thread(target=back_process,args=[research])
            list_thread[research.id].setDaemon(True)
            list_thread[research.id].start()
            time.sleep(3600)

def check(research):
    """we check if the thread of the research is alive"""
    
    #we check if the research was already done
    if research.is_finish:
        return False

    #we check if the research is currently running
    if not research.is_running:
        return False

    # we check if there is a thread for the research
    if not research.id in list_thread:
        return False
    
    #we check if the thread is running
    if list_thread[research.id].is_alive():
        return True
    else:
        return False

def delete(research):
    
    #we delete in the database
    Research.objects.filter(id=research.id).delete()
    
    #we delete all intermediate file 
    for file in glob(f'{TEMPORARY_DATA}/*research_{research.id}*'):
        os.remove(file)

    #we delete html plot of the research
    for file in glob(f'UI_Front/templates/*research_{research.id}*'):
        os.remove(file)

    return True

