import time
#urllib2 is used to simulate online files as local files
from urllib.request import urlopen
#ElementTree is used for xml parsing
from lxml import etree as ET

#numpy is used for better arrays
import numpy as np
from DataBase.models import Article_Job, Article_Step
#unidecoed is for removing accents
import unidecode as UN

import DataBase.functions.PDF_download as pdf
from DataBase.functions.Remove_references import remove_references
from DataBase.functions.filter_article import split_search_term

from DataBase.models import *

from programmeDjango.settings import ARTICLE_DATA

from threading import Thread

def get_search_term(search):
    """we translate the search to a readable string search for the api"""
    split,_ = split_search_term(search)
    search_term = ''
    for c in split:
        search_term += c
        search_term += "+"
    
    search_term = search_term.replace(" ","+")
    return search_term

def get_max_article(search):

    api_query = 'http://export.arxiv.org/api/query?search_query='
    search_term = get_search_term(search)

    query_base = api_query + search_term
     
    response = urlopen(query_base)
    xml_doc = ET.fromstring(response.read())

    total = xml_doc[4].text
    total = int(total)

    return total

def Get_ID(search_term,research):
   
    #sets the location of the API for the query
    api_query = 'http://export.arxiv.org/api/query?search_query='
 
    #creates the query to the DB to get the number of papers matching the
    #   search_term:    
    #   1)Creates the base query
    #   2)Parses the response to get the total number of pages and papers
    query_base = api_query + search_term
    
    arXID = []
    #all IDs are stored in the XML response of query, we parse the XML
    #   extract the arxID from the it, and add it to a ID_list
    #gets the XML respon
    
    try:
        
        response = urlopen(query_base)
        xml_doc = ET.fromstring(response.read())
        
    except:
        return False

    total = xml_doc[4].text
    total = int(total)

    article_by_page = 10000
    page = int(total/10000) + 1

    for i in range(page):
        
        if Article_Job.objects.filter(research=research,type="page",job=str(i)).exists():
            continue

        try:
            response = urlopen(query_base + '&start=' + str(i*article_by_page) + '&max_results='+str(article_by_page))       
            xml_doc = ET.fromstring(response.read())
        except:
            continue

        for child in xml_doc:
            begin = child.tag.split('}')[0]+ '}'
            break 
            
        for ID in xml_doc.findall('.//' + begin + 'id'):
            #if the ID is not in the list already, then we add it to the list
            if 'abs' in ID.text:
                temp_ID = ID.text.split('abs/')[1].split('v')[0]
                arXID.append(temp_ID)
                Article_Job.objects.create(research=research,type="id",job=str(temp_ID))

        Article_Job.objects.create(research=research,type="page",job=str(i))

    return arXID

def extract_article(id_list,research):
    """ Extract MetaData and abstract for an article. Return Date, Journal, Title, Authors, Aff, Abs, DOI.
        In production, we give the url to fetch the xml file but during test, we give a xml file."""

    #url where we fetch data
    api_fetch = 'http://export.arxiv.org/api/query?id_list='
    for ID in id_list:

        if Article_Job.objects.filter(research=research,type="id_done",job=str(ID)).exists():
            continue
        # we check if research still exists
        
        URL = 'http://arxiv.org/pdf/' + str(ID) + '.pdf'
        fetch = api_fetch + ID 
        # Extracts data from xml   
        begin_sub = ''
        try:
            response = urlopen(fetch)       
            xml_doc = ET.fromstring(response.read())
            for child in xml_doc:
                begin = child.tag.split('}')[0]+ '}'
                for subchild in child:
                    if subchild.tag.split('}')[0]+ '}' != begin:
                        begin_sub = subchild.tag.split('}')[0]+ '}'
                        break
        except:
            continue
        
        #Extracts the DOI, not always available
        doi = ''
        for tag in xml_doc.findall('.//'+ begin_sub + 'doi'):
            doi = tag.text
        #we check if the article is already in database with the doi
        article = Article.objects.filter(doi=doi)
        if not doi == '' and article.exists():
            article = article[0]
            Research_Article.objects.create(research=research,article=article)
            #we check if the pdf is in local
            if not article.is_file_get:
                is_download = pdf.download_from_URL(article)
                if is_download:
                    article.is_file_get = True
                    article.save()
            continue
         
        #Extracts the date from the XML, always available
        date = ''
        for tag in xml_doc.findall('.//'+ begin + 'published'):
            date = tag.text.split('T')[0]
            date = datetime.datetime.strptime(str(date),"%Y-%m-%d").date()
        if date != '':
            Date = date
        else:
            Date = np.nan
        
        #Extracts the title of the paper, always available
        title = ''
        for tag in xml_doc.findall('.//'+ begin + 'title'):
            if 'ArXiv' not in tag.text:
                title = tag.text                                 
        if title != '' and title != None:
            Title = UN.unidecode(title)
        else:
            Title = np.nan
        #Extract the names of the Authors, not always available
        authors = []
        for tag in xml_doc.findall('.//' + begin + 'name'):
            if (tag.text != None) and (tag.text != ''):
                last_name = tag.text.split(" ")[-1] 
                first_name = tag.text.split(" ")[0:-1]

                authors.append((last_name,first_name))
        
        #Extracts the full abstract not always available
        abstract = ''
        for tag in xml_doc.findall('.//' + begin + 'summary'):
            abstract = tag.text
        if abstract != '' and abstract != None:
            Abstract = UN.unidecode(" ".join(abstract.split()))
        else:
            Abstract = ''


        # we write the article in database
        article = ''
        is_file_get = False
        if doi == '' or not Article.objects.filter(doi=doi).exists():
            article = Article.objects.create(title=title,doi=doi,abstract=abstract,publication=Date,url_file=URL)
            try:
                full_text = pdf.extract_full_text(article)
                is_file_get = True
                full_text = remove_references(full_text)
            except:
                full_text = ""
            article.full_text = full_text.replace("\x00", "\uFFFD")
            article.is_file_get = is_file_get
            article.save()
        else:
            article = Article.objects.filter(doi=doi)[0]
        
        # we bind to the research
        Research_Article.objects.create(research=research,article=article)

        # we add the author
        for author in authors:
            #we check if the author exist
            a = Author.objects.filter(last_name = author[0],first_name = author[1])
            if a.exists():
                author = a[0]
            else:
                author = Author.objects.create(last_name=author[0],first_name=author[1])
            # we binde the author the the article
            Article_Author.objects.create(article=article,author=author)
        
        Article_Job.objects.create(research=research,type="id_done",job=str(ID))


def get_article(search, research,begin,end, number_threads=1):
    
    #sets the location of the API for the fetching
    api_fetch = 'http://export.arxiv.org/api/query?id_list='

    step_article = Article_Step.objects.get(research=research)
    if Article_Step.objects.get(research=research).step == "":
        step_article.step = "get_id"
        step_article.save()

    ID_list= []
    if step_article.step == "get_id":
        # we split the search string in individual element
        search_term = get_search_term(search)
        ID_list = Get_ID(search_term,research)
        if ID_list == False:
            time.sleep(1)
            ID_list = Get_ID(search_term)
            if ID_list == False:
                return False
        
        step_article.step = "extract_metadata"
        step_article.save()

    if step_article.step == "extract_metadata":
        # we distribute the job to the threads
        
        list_job = []
        for i in range(number_threads):
            list_job.append([])
        if ID_list == []:
            ID_list = Article_Job.objects.filter(research=research,type="id").values_list("job", flat=True)

        for i in range(len(ID_list)):
            current_thread = i % number_threads
            list_job[current_thread].append(ID_list[i])
        
        # we create the threads
        list_threads = []
        for i in range(number_threads):
            list_threads.append(Thread(target=extract_article,args=(list_job[i],research)))
            

        # we start the thread and wait it finish
        for thread in list_threads:
            thread.start()
        for thread in list_threads:
            thread.join()

        