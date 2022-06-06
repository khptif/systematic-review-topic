#urllib2 is used to simulate online files as local files
from urllib.request import urlopen
#ElementTree is used for xml parsing
from lxml import etree as ET
#pandas is used for easy data analysis
import pandas as pd
#numpy is used for better arrays
import numpy as np
#unidecoed is for removing accents
import unidecode as UN
import BackEnd.functions.PDF_download as pdf
from BackEnd.functions.Remove_references import *

from threading import Thread

from DataBase.models import *
from BackEnd.functions.filter_article import split_search_term
db = 'pmc'

def get_search_term(search):
    """we translate the search to a readable string search for the api"""
    split,_ = split_search_term(search)
    search_term = ''
    for c in split:
        search_term += c
        search_term += "+"
    
    return search_term.replace(" ","+")

def get_max_article(search):
    """we give the max article of this research"""
    search_term = get_search_term(search)

    api_query = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
    api_query = api_query + "db=" + db + "&term=" + search_term

    #gets the XML response
    xml_doc = ET.parse(urlopen(api_query)).getroot()

    #gets the content of the tag Count (number of papers)   
    max_article = int(xml_doc.find('Count').text)

    return max_article

def get_ID(search):
    """ return a list of id of article"""
    api_query = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
    search_term = get_search_term(search)
    query_base = api_query + 'db=' + db + '&term=' + search_term

    #gets the XML response
    xml_doc = ET.parse(urlopen(query_base)).getroot()
    #gets the content of the tag Count (number of papers)   
    max_pages = int(xml_doc.find('Count').text)

    #by default, a query to the DB returns 20 results, so we adapt
    #   the query based on the number of total papers found by
    #   the basic search, so that instead of making total/20 queries,
    #   we just make 2 (gain of time of factor 60)!
    query = query_base + '&RetMax=' + str(max_pages)
    xml_doc = ET.parse(urlopen(query)).getroot()

    ID_list = []
    for ID in xml_doc.iter('Id'):
        ID_list.append(ID.text)

    return ID_list

def extract_metadata(id):
    """ extract metadata from the id input and return a dictionnary with these data"""
    #Gets the xml with all meta-data
    api_fetch = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'
    fetch = api_fetch + 'db=' + db + '&id=' + str(id) 
    
    try:
        xml_doc = ET.parse(urlopen(fetch)).getroot()
    except:
        return False


    #Removes all unnecessary data (Tables, captions and figure related tags)
    ET.strip_elements(xml_doc, 'xref','table-wrap','fig', with_tail=False)
    #Extracts the date from the XML, always available

    # we extract de doi
    doi = ''
    doi_parent = xml_doc.find("article").find("front").find("article-meta")

    for child in doi_parent:
        if child.tag == "article-id" and child.attrib['pub-id-type'] == "doi":
            doi = child.text
            break
    
    # we extract the date of the publication
    date = ''
    year = 0
    month = 0
    day = 0

    try:
        for tag in xml_doc.iter('year'):
            year = int(tag.text)
            break
        for tag in xml_doc.iter('month'):
            month = int(tag.text)
            break
        for tag in xml_doc.iter('day'):
            day = int(tag.text)
        date = datetime.date(year,month,day)
    except:
        date = datetime.date(1900,1,1)
    
    #Extracts the title of the paper, always available
    title = ''
    for tag in xml_doc.iter('title-group'):
        title = tag.find('article-title').text
    if title is None:
        print(" title none: " + fetch)
        title = ''
    
    #Extract the names of the Authors, always available
    # we return a list in the format (last name, first name)

    author = []
    for tags in xml_doc.iter('contrib'):
        for tag in tags.iter('name'):
            last_name=''
            first_name=''
            try:
                last_name = tag.find('surname').text
            except AttributeError:
                pass
            #Sometimes only the surname is given, nit the names
            try:
                first_name = tag.find('given-names').text
            except AttributeError:
                pass
            except TypeError:
                pass
            author.append((last_name,first_name))

    
    #Extracts the full abstract (itertext takes all text between the abstract tags, so we
    #   remove all \n characters and all superfluous spaces), not always available
    abstract = ''
    for tag in xml_doc.iter('abstract'):
        a = "".join(tag.itertext()).replace('\n','')
        if a != '' and a != None:
            abstract += UN.unidecode(" ".join(a.split())) + " "
   
    #Extracts the url of the full text
    url = ''
    if not doi == '':
        url = pdf.get_URL_from_DOI(doi)

        
    return {"title":title,"doi":doi,'date':date,'author':author,'abstract':abstract,'url':url}


def get_article_parallel(research,ID_list):
    """ we get write the article in our database """

    for id in ID_list:
        # we extract metadata
        metadata = extract_metadata(id)
        #we check if we have this article with the doi
        article = Article.objects.filter(doi=metadata["doi"])
        if article.exists():
            Research_Article.objects.create(research=research,article=article[0])
            continue

        #we extract the pdf
        try:
            full_text = pdf.extract_full_text(metadata['url'],"pmc_article_"+str(id)+"_research_"+str(research.id))
            full_text = remove_references(full_text)
        except:
            full_text = ""

        #we create the article
        article = Article.objects.create(title=metadata['title'],doi=metadata['doi'],abstract=metadata['abstract'],full_text=full_text,publication=metadata['date'],url_file=metadata['url'])
        
        # we bind it to the research
        Research_Article.objects.create(research=research,article=article)

        # we create the authors
        author_list = metadata["author"]

        for author in author_list:
            # we check if the author exist already in our database
            a = Author.objects.filter(last_name=author[0],first_name=author[1])
            if a.exists():
                #we bind the author to the article
                Article_Author.objects.create(article=article,author=a[0])
            else:
                author = Author.objects.create(last_name = author[0],first_name = author[1])
                Article_Author.objects.create(article=article,author=author)

def get_article(search,research,number_threads=1):

    # we configure the search_term
    search_term = get_search_term(search)

    #we get the list of id of articles
    list_id = get_ID(search)

    #we distribute the id
    Thread_id = []
    number_id_by_thread = int(len(list_id)/number_threads)
    begin = 0
    end = 0
    # we build the threads
    for thread in range(number_threads):
        end = begin + number_id_by_thread
        Thread_id.append(Thread(target=get_article_parallel,args=(research,list_id[begin:end])))
        begin = end
    # we build the last thread with the last id
    
    Thread_id.append(Thread(target=get_article_parallel,args=(research,list_id[begin:])))

    # we start the threads

    for thread in Thread_id:
        thread.start()
    
    # we wait the thread finish
    for thread in Thread_id:
        thread.join()
    