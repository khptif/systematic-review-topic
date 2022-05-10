import sys, os, time
#urllib2 is used to simulate online files as local files
from urllib.request import urlopen
#ElementTree is used for xml parsing
from lxml import etree as ET

#numpy is used for better arrays
import numpy as np
#unidecoed is for removing accents
import unidecode as UN

import BackEnd.functions.PDF_download as pdf
import BackEnd.functions.filter_article as filter

def extract_metaData(fetch_url='',xml_data='',test=False):
    """ Extract MetaData and abstract for an article. Return Date, Journal, Title, Authors, Aff, Abs, DOI.
        In production, we give the url to fetch the xml file but during test, we give a xml file."""

   
    # return data
    DOI = ''
    Date = ''
    Journal = ''
    Title = ''
    Authors = ''
    Aff = ''
    Abstract = ''

    #url where we fetch data
    fetch = fetch_url

    # Extracts data from xml   
    begin_sub = ''
    try:
        response = ''
        if test:
            response = xml_data
        else:
            response = urlopen(fetch)       
        xml_doc = ET.fromstring(response.read())
        for child in xml_doc:
            begin = child.tag.split('}')[0]+ '}'
            for subchild in child:
                if subchild.tag.split('}')[0]+ '}' != begin:
                    begin_sub = subchild.tag.split('}')[0]+ '}'
                    break
    except:
        xml_doc = ET.fromstring("<root>blabla</root>")

    #Extracts the DOI, not always available
    doi = ''
    for tag in xml_doc.findall('.//'+ begin_sub + 'doi'):
        doi = tag.text
    if doi != '':
        DOI = doi
    else:
        DOI = np.nan

    #Extracts the date from the XML, always available
    date = ''
    for tag in xml_doc.findall('.//'+ begin + 'published'):
        date = tag.text.split('T')[0]
        date = date.split('-')[0] + '-' + date.split('-')[1]
    if date != '':
        Date = date
    else:
        Date = np.nan
    #Extracts the journal name, not always available
    journ = ''
    for tag in xml_doc.findall('.//' + begin_sub + 'journal_ref'):
        journ = tag.text
    if journ != '' and journ != None:
        Journal = UN.unidecode(journ)
    else:
        Journal = np.nan
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
    author = []
    for tag in xml_doc.findall('.//' + begin + 'name'):
        if (tag.text != None) and (tag.text != ''):
            full_name = tag.text.split()[-1] + ' ' + tag.text.split()[0]
            author.append(UN.unidecode(full_name))
    if len(author) != 0:
        for a in author:
            Authors += ";".join(a)
    else:
        Authors = np.nan
    #Extracts the corresponding affiliations not always available
    affiliation = []
    for tag in xml_doc.findall('.//'+ begin_sub + 'affiliation'):
        temp = tag.text.split(';')
        for item in temp:
            if item not in affiliation:
                try:
                    affiliation.append(UN.unidecode(item))
                except AttributeError:
                    pass
    if len(affiliation) !=0:
        Aff = ";".join(affiliation)
    else:
        Aff = np.nan
    #Extracts the full abstract not always available
    abstract = ''
    for tag in xml_doc.findall('.//' + begin + 'summary'):
        abstract = tag.text
    if abstract != '' and abstract != None:
        Abstract = UN.unidecode(" ".join(abstract.split()))
    else:
        Abstract = np.nan
    
    return Date, Journal, Title, Authors, Aff, Abstract, DOI



def Get_ID(search_term):
   
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
    
    for i in range (10):
        response = urlopen(query_base + '&start=' + str(i*10000) + '&max_results=10000')       
        xml_doc = ET.fromstring(response.read())

        for child in xml_doc:
            begin = child.tag.split('}')[0]+ '}'
            break 
            
        for ID in xml_doc.findall('.//' + begin + 'id'):
            #if the ID is not in the list already, then we add it to the list
            if 'abs' in ID.text:
                temp_ID = ID.text.split('abs/')[1].split('v')[0]
                arXID.append(temp_ID)
    return arXID

def Get_arXiV(search_term, name):
    
    #sets the location of the API for the fetching
    api_fetch = 'http://export.arxiv.org/api/query?id_list='

    # we split the search string in individual element
    search_term_split, keywords = filter.split_search_term(search_term)
    
    print("get all id key")
    #for every key word, we make a research and extract all id article from this keyword
    for key,_ in keywords.items():
        keywords[key] = Get_ID(key)

    print("id article done")
    arXID = filter.parsing(search_term_split,keywords)
    print("number final id: " + str(len(arXID)))
    
    #1 - Extracts the informaation
    Date, Journal, Title, Authors, Aff, Abs, MesH,FullT, DOI = \
                            [],[], [], [], [], [], [], [], []
    Fetched = []
    URL = []
    dump_in = 0
    print ('Extracting the data for the set of the request')
    if os.path.exists("results/"+name):
        os.remove("BackEnd/functions/results/"+name)
    results_file = open("BackEnd/functions/results/"+name,"a")
    size = len(arXID)
    current = 0
    for ID in arXID:
        print("\r" + str(current) +"/" +str(size), end='')
        URL = 'http://arxiv.org/pdf/' + ID + '.pdf'
        fetch = api_fetch + ID 
        Date, Journal, Title, Authors, Aff, Abstract, DOI = extract_metaData(fetch)
        Full_Text = pdf.extract_full_text(URL,"arx")

        results_file.write("Title: "+Title + "\n")
        results_file.write("Authors: " + Authors + "\n")
        results_file.write("DOI: " + str(DOI) + "\n")
        results_file.write("Abstract :" + "\n" + Abstract + "\n")
        
        results_file.write("Full_Text: " + "\n" + str(Full_Text) + "\n")
        current += 1

    
    results_file.close()

    return True

# for test
if __name__ == "__main__":
    import sys
    term = sys.argv[1]
    name = sys.argv[2]
    print(Get_arXiV(term, name))
    
