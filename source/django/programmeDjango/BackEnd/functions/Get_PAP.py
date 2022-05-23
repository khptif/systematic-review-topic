
import requests
#numpy is used for better arrays
import numpy as np
#Time for waiting
import time
from BackEnd.functions.filter_article import split_search_term
#unidecoed is for removing accents
import unidecode as UN
import datetime

from DataBase.models import *

#Downloading PDF
import BackEnd.functions.PDF_download as pdf

from threading import Thread

from BackEnd.functions.Remove_references import remove_references

def get_search_term(search):
    """we translate the search to a readable string search for the api"""
    split,_ = split_search_term(search)
    search_term = ''
    for c in split:
        search_term += c
        search_term += "+"
    
    return search_term

def get_max_article(search_term):
    api_query = 'http://paperity.org/api/1.0/search/'

    
    query_base = api_query + '?text=' + search_term
    json_data = requests.get(query_base).json() 
    total = json_data['total']
    return total

def extract_metadata(ID):
    api_fetch = 'http://paperity.org/api/1.0/p/'
    url_fetch = api_fetch + str(ID)

    try:
        json_data = requests.get(url_fetch).json()
    except:
        try:
            time.sleep(1)
            json_data = requests.get(url_fetch).json()
        except:
            return False
          
    #Gets the DOI
    DOI = ''
    if json_data['paper']['doi'] != None:
        DOI = json_data['paper']['doi']
    else:
        DOI = np.nan
        
    #Gets the date
    Date = ''
    if json_data['paper']['date'] != None:
        Date = json_data['paper']['date']
    else:
        Date = np.nan

    #Gets the title of the paper
    Title = ''
    if json_data['paper']['title'] != None:
        Title = (UN.unidecode(json_data['paper']['title']))
    else:
        Title = (np.nan)

    #Gets the  author list
    # we return a list of authors in this format: (last_name, first_name)
    Authors = []
    if json_data['paper']['authors_10'] != None:
        authors_request_data= json_data['paper']['authors_10']
        author = []
        for items in authors_request_data:
            # the last is "et al." so we don't take it
            if items == "et al.":
                continue

            names = items.split(",")
            # we check if we have at most two element otherwise, if there are a error, this method bug
            if len(names) >= 2:
                author.append((UN.unidecode(names[0]),UN.unidecode(names[1][1:])))
        
        Authors = author
    else:
        Authors = np.nan

    #Gets the abstract
    Abstract = ''
    if json_data['paper']['abstract'] != None:
        Abstract = (UN.unidecode(json_data['paper']['abstract']))
    else:
        Abstract = (np.nan)

       
    #Gets the URL
    URL = ''
    if json_data['paper']['url_pdf'] != None:
        URL = (json_data['paper']['url_pdf'])
            
    else:
        URL = (np.nan)

    #Wait 1s before making another request, as demanded by paperity staff
    #time.sleep(1.1)
    return {"title": Title,"date": Date,"doi": DOI, "authors": Authors, "abstract": Abstract,"url": URL}

def get_article_parallel(begin_page,number_page,research,search_term):
    """ the method to parallelize in order to extract all article metadata
        begin_page: where to start, 
        number_page: how many page to process,
        research: the object research bound to this search,
        search_term: the string to send to api,
        api_query: the url for the api"""

    api_query='http://paperity.org/api/1.0/search/'
    for i in range(begin_page, begin_page + number_page):
        
        query_base = api_query + str(i) + '?text=' + search_term
        json_data = ''
        bad_request = False
        for i in range(3):
            try:
                bad_request = True
                json_data = requests.get(query_base).json()
                bad_request = False
                break
            except:
                time.sleep(1)
                continue

        if bad_request :
            continue

        for paper in json_data['papers']:
            #we save the metadata in our database
            id = paper['pid']
            metadata = extract_metadata(id)

            if metadata == False:
                time.sleep(1)
                metadata = extract_metadata(id)
                if metadata == False:
                    continue

            doi = metadata['doi']
            publication = datetime.datetime.strptime(metadata["date"],'%Y-%m-%d').date()
            authors = metadata['authors']

            #we create the article we check if exist already by doi
            article = Article.objects.filter(doi=doi)

            if article.exists():
                article = article[0]
            else:
                try:
                    full_text = pdf.extract_full_text(metadata['url'],"papetery_page_"+str(i)+ "_article_"+str(id)+"_research_"+str(research.id))
                    full_text = remove_references(full_text)
                except:
                    full_text = ""
                title = metadata['title']
                abstract = metadata['abstract']
                url_file = metadata['url']
                article = Article(title=title,doi=doi,abstract=abstract,full_text=full_text,publication=publication,url_file=url_file)

            article.save()
            Research_Article.objects.create(research=research,article=article)

            author_list = []
            # we create the authors and associate to the article
            for a in authors:
                last_name = a[0]
                first_name = a[1]

                #we check if authors exist already
                author = Author.objects.filter(last_name=last_name,first_name=first_name)
                if author.exists():
                    author = author[0]
                else:
                    author = Author(last_name=last_name,first_name=first_name)
                author_list.append(author)

                for author in author_list:
                    author.save()
                    Article_Author.objects.create(author=author,article=article)
            
                
        #Wait 1s before making anothe request, as demanded by paperity staff
        #time.sleep(1.1)

def get_article(search,research,number_threads = 1,test_number_page=0,test=False):
    #sets the location of the API for the query
    api_query = 'http://paperity.org/api/1.0/search/'
    #sets the location of the API for the fetching
    api_fetch = 'http://paperity.org/api/1.0/p/'
    
    search_term = get_search_term(search)

    max_page = test_number_page
    if(max_page == 0):
        query_base = api_query + '?text=' + search_term
        #gets the response to extract the total number of papers
        json_data = requests.get(query_base).json()
   
        total = json_data['total']
        item_per_page = json_data['items_per_page']
        #gets the maximum pages. Paperity does 20 per page, impossible to change
        max_page = int(total/item_per_page) + 1


    # distribute the jobs through threads
    Thread_id = []
    number_page_by_thread = int(max_page/number_threads)
    assigned_page = 0
    current_page = 1

    # we build the threads
    for thread in range(number_threads):
        begin = current_page
        Thread_id.append(Thread(target=get_article_parallel,args=(begin,number_page_by_thread,research,search_term)))
        current_page += number_page_by_thread
    # we build the last thread with the last pages
    begin = current_page
    last_pages = max_page - current_page
    Thread_id.append(Thread(target=get_article_parallel,args=(begin,last_pages,research,search_term)))

    # we start the threads

    for thread in Thread_id:
        thread.start()
    
    # we wait the thread finish
    for thread in Thread_id:
        thread.join()
    
