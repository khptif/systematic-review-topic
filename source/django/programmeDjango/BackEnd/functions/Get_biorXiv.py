from datetime import datetime
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup

import BackEnd.functions.PDF_download as pdf
from BackEnd.functions.Remove_references import remove_references
from BackEnd.functions.filter_article import split_search_term

from DataBase.models import *
from BackEnd.models import *

from threading import Thread

from programmeDjango.settings import ARTICLE_DATA

def get_search_term(search):
    """we translate the search to a readable string search for the api"""
    split,_ = split_search_term(search)
    search_term = ''
    for c in split:
        search_term += c
        search_term += "+"
    
    return search_term

def get_max_article(search,begin,end):

    year_begin = str(begin.year)
    month_begin = str(begin.month)
    day_begin = str(begin.day)

    year_end = str(end.year)
    month_end = str(end.month)
    day_end = str(end.day)

    search_term = get_search_term(search)
    api_query = 'https://www.biorxiv.org/search/'
    query_base = api_query + search_term + f"+limit_from:{year_begin}-{month_begin}-{day_begin}+limit_to:{year_end}-{month_end}-{day_end}+"
    
    first_page_query = query_base
    text = requests.get(first_page_query).text
    soup = BeautifulSoup(text, 'html.parser')
    try:
        last_str = soup.select_one('li.pager-last.last.odd a').string    
        num_pages = int(last_str)
    except:
        try:
            last_str = soup.select_one('li.pager-item.last.odd a').string    
            num_pages = int(last_str)
        except:
            num_pages = 1

    article_by_page=10
    return article_by_page * num_pages

def extract_id(search_term,research,begin,end):
    """ 
    input: search_term is the string that is send to the biorxiv.
    output: a list of all the id article from biorxiv,
            a dictionnary where the key is id article and value is the html code of the article. It corresponds to each entry.
    """
    year_begin = str(begin.year)
    month_begin = str(begin.month)
    day_begin = str(begin.day)

    year_end = str(end.year)
    month_end = str(end.month)
    day_end = str(end.day)

    api_query = 'https://www.biorxiv.org/search/'
    query_base = api_query + search_term + f"+limit_from:{year_begin}-{month_begin}-{day_begin}+limit_to:{year_end}-{month_end}-{day_end}+"
    
    list_entry = []
    
    first_page_query = query_base
    try:
        text = requests.get(first_page_query).text
    except:
        return [],{}
    soup = BeautifulSoup(text, 'html.parser')
    try:
        last_str = soup.select_one('li.pager-last.last.odd a').string    
        num_pages = int(last_str)
    except:
        try:
            last_str = soup.select_one('li.pager-item.last.odd a').string    
            num_pages = int(last_str)
        except:
            num_pages = 1
    for i in range(num_pages):

        if Article_Job.objects.filter(research=research,type="page",job=str(i)).exists():
            continue

        query = query_base if i == 0 else query_base + '?page=' + str(i)
        try:
            text = requests.get(query).text
        except:
            continue
        
        soup = BeautifulSoup(text, 'html.parser')
        entries = soup.select('div.highwire-article-citation')

        for entry in entries:
            Article_Job.objects.create(research=research,type="entry",job=str(entry))
            list_entry.append(entry)

        Article_Job.objects.create(research=research,type="page",job=str(i))

    return list_entry


def extract_article(entry_list,research):
    """ input:  a list of entry_id, 
                the dictionnary with all entry and the research.
        For each id, we write the article and all data in our database"""
    
   
    for entry in entry_list:
        
        if Article_Job.objects.filter(research=research,type="entry_done",job=str(entry)).exists():
            continue

        doi_url = str(entry.select_one(".highwire-cite-metadata-doi").contents[1]).strip()
        doi = doi_url.replace("https://doi.org/", "")

        #we check if the article is already in database
        a= Article.objects.filter(doi = doi)
        if a.exists():
            Research_Article.objects.create(research=research,article=a[0])
            # we check if the pdf exists in local
            if not a[0].is_file_get:
                is_download = pdf.download_from_URL(a[0].url_file,ARTICLE_DATA + "/" +pdf.name_article_pdf(a[0]))
                if is_download:
                    a[0].is_file_get = True
                    a[0].save()
            Article_Job.objects.filter(research=research,type="entry",job=str(entry)).delete()
            continue

        authors_list = []
        for author_html in entry.select(".highwire-citation-author"):
            
            try:
                first_name = author_html.select_one(".nlm-given-names").string
                last_name = author_html.select_one(".nlm-surname").string
                authors_list.append((last_name,first_name))
            except:
                continue

        date_str = entry.select_one(".highwire-cite-metadata-pages").string[0:10]
        publication = ''
        try:
            publication = datetime.datetime.strptime(date_str,"%Y.%m.%d").date()
        except:
            publication = datetime.date(1800,1,1)

        try:
            title_sel = entry.select_one('.highwire-cite-linked-title')
            title = title_sel.text
            abstract_url = "https://www.biorxiv.org" + str(title_sel["href"])
            url = abstract_url + ".full.pdf"
        except:
            url = ""

        abstract = ''
        try:
            abstract_page = requests.get(abstract_url).text
            soup = BeautifulSoup(abstract_page, 'html.parser')
            sel = soup.select_one('div#abstract-1 p').text
            abstract =  sel
        except:
            abstract = ''
            
        #we write the article. We check if the article exist already. We check by doi.
        article = Article.objects.filter(doi = doi)
        is_file_get = False
        if article.exists():
            article = article[0]
        else:
            article = Article.objects.create(title=title,doi=doi,abstract=abstract,publication=publication,url_file=url)
            try:
                name = pdf.name_article_pdf(article)
                full_text = pdf.extract_full_text(url,name)
                full_text = remove_references(full_text)
                is_file_get = True
            except:
                full_text = ""
            article.full_text = full_text.replace("\x00", "\uFFFD")
            article.is_file_get = is_file_get
            article.save()

        # we bond the article to the research
        Research_Article.objects.create(research=research,article=article)

        # we write the authors and bind to the article
        for author in authors_list:
            
            a = Author.objects.filter(last_name = author[0],first_name = author[1])
            if a.exists():
                author = a[0]
            else:
                author = Author.objects.create(last_name=author[0],first_name=author[1])
            Article_Author.objects.create(article=article,author=author)

        Article_Job.objects.create(research=research,type="entry_done",job=str(entry))
        

def get_article( search, research, begin,end,number_thread=1):
    """ we get the article and write them in database. The process is parallelized"""

    article_step = Article_Step.objects.get(research=research)
    if article_step.step == "":
        article_step.step = "entry"
    

    entry = []
    if article_step.step == "entry":
        search_term = get_search_term(search)
        entry = extract_id(search_term,research,begin,end)
        article_step.step = "extract"
       
    if article_step.step == "extract":
    #we distribute the job to each thread
        list_job = []
        for i in range(number_thread):
            list_job.append([])
        
        if entry == []:
            entry_list = Article_Job.objects.filter(research=research,type="entry").values_list("job",flat=True)
            for i in entry_list:
                entry.append(BeautifulSoup(i,'html.parser'))

        for i in range(len(entry)):
            current_thread = i % number_thread
            list_job[current_thread].append(entry[i])
    
        #we create the threads
        list_thread = []
        for i in range(number_thread):
            list_thread.append(Thread(target=extract_article,args=(list_job[i],research)))
    
        # we start the threads and wait they finish
        for thread in list_thread:
            thread.start()
        for thread in list_thread:
            thread.join()



