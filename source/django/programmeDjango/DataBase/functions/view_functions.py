
from DataBase.models import *
from DataBase.functions.Get_arXiV import get_article as arxiv,get_max_article as max_arxiv
from DataBase.functions.Get_biorXiv import get_article as biorxiv, get_max_article as max_biorxiv
from DataBase.functions.Get_medrXiv import get_article as medrxiv, get_max_article as max_medrxiv
from DataBase.functions.Get_PAP import get_article as pap, get_max_article as max_pap
from DataBase.functions.Get_PMC import get_article as pmc, get_max_article as max_pmc
from DataBase.functions.Get_PM import get_article as pm, get_max_article as max_pm

import zipfile
from programmeDjango.settings import TEMPORARY_DATA,ARTICLE_DATA
import glob
import os
import sys
from threading import Thread

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
        #article += max_pap(search,begin,end) 
        pass
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
        research.current_article_db = "PMC"
        research.save()
        #research.current_article_db = "paperity"
        #research.save()

    # for now we pass the paperity database beacause it's too long
    #if research.current_article_db == "paperity":
    if False:

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

def create_final_file(research,user):
    #we create a zip file with all article checked in TableChoice
    #and return the name of the file

    #we create the zip file
    path_zip = TEMPORARY_DATA + "/research_{id}_final.zip".format(id=str(research.id))
    zip_file = zipfile.ZipFile(path_zip,mode="w")
    
    #we get the articles
    list_tablechoice = TableChoice.objects.filter(research=research,user=user,is_check=True)
    # for each article, we will put in the directory that represent his own cluster
   
    for row in list_tablechoice:

        article = row.article
        #we get the cluster object of this research and article
        cluster = Cluster.objects.filter(research=research,article=article)
        #we check if exist
        if not cluster.exists():
            continue
        else:
            cluster = cluster[0]
        
        #we get the file to the article
        files = glob.glob(ARTICLE_DATA + "/article_{id}_*.pdf".format(id=str(article.id)))

        file_exist = False
        #we check if the pdf article exists
        if len(files) > 0:
            #we get his pathname
            path_to_article = os.path.abspath(files[0])
            file_exist = True

        else:
            path_to_article = TEMPORARY_DATA + "/research_{id_research}_user_{id_user}_article_{id_article}.txt".format(id_research = research.id,id_user = user.id,id_article = article.id)
            #we create a little file .txt with information about the article
            f = open(path_to_article,mode="w")

            try:
                #we write the title, doi, url, author and abstract
                f.write(article.title + "\n\n")
                if article.doi is None:
                    article.doi = ""
                f.write("DOI: " + article.doi + "\n\n")
                if article.url_file is None:
                    article.url_file = ""
                f.write("URL: " + article.url_file + "\n\n")

                author_string = ""
                for author in Author.objects.filter(article_author__article = article):
                    author_string += author.last_name + " " + author.first_name + ";\n"

                f.write("Authors: \n" + author_string + "\n\n")
                f.write("Abstract \n" + article.abstract)
            finally:
                f.close()

        #we add the article to the zip file
        topic = cluster.topic.replace(" ","").replace(",","_")
        if len(topic) > 128:
            topic = topic[0:128]
        
        file_name = article.title.replace(" ","_")
        if len(file_name) > 128:
            file_name = file_name[0:128]
        
        if file_exist:
            file_name += ".pdf"
        else:
            file_name += ".txt"
            
        zip_file.write(path_to_article,"{topic}/{file_name}".format(topic=topic,file_name=file_name))
    
    zip_file.close()
    # we delete all temporary file
    files_delete = glob.glob(TEMPORARY_DATA + "/research_{id_research}_user_{id_user}_article_*.txt".format(id_research = research.id,id_user = user.id))
    for f in files_delete:
        #we check if exist before
        os.remove(f)
    
    return path_zip