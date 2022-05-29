
import sys, os, time
#urllib2 is used to simulate online files as local files
from urllib.request import urlopen
import requests
#ElementTree is used for xml parsing
from lxml import etree as ET
#pandas is used for easy data analysis
import pandas as pd
#numpy is used for better arrays
import numpy as np
#unidecoed is for removing accents
import unidecode as UN
#SQLAlchemy is for database management
from sqlalchemy import create_engine
from PDF_download import *

from DataBase.models import *
from filter_article import split_search_term
db = 'pmc'

def get_search_term(search):
    """we translate the search to a readable string search for the api"""
    split,_ = split_search_term(search)
    search_term = ''
    for c in split:
        search_term += c
        search_term += "+"
    
    return search_term

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

def extract_data(id):
    
    url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/idconv.fcgi?ids=' +\
              id +'&idtype=pmcid&format=json&versions=no&showaiid=no'
    #Gets the JSON response
    doi=''
    try:
        json_data = requests.get(url).json()
        #Extracts PMID and DOI for each entry
        for ID in json_data['records']:
            if 'doi' in ID:
                doi = ID['doi']
    except:
        pass
    
    #Gets the xml with all meta-data
    api_fetch = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'
    fetch = api_fetch + db + '&id=' + ID 
    
    try:
        xml_doc = ET.parse(urlopen(fetch)).getroot()
    except:
        xml_doc = ET.fromstring("<root>blabla</root>")


    #Removes all unnecessary data (Tables, captions and figure related tags)
    ET.strip_elements(xml_doc, 'xref','table-wrap','fig', with_tail=False)
    #Extracts the date from the XML, always available

    doi = ''
    list_doi = xml_doc.findall("front")[0].findall("[@pub-id-type='doi']")
    if not len(list_doi)<= 0:
        doi = list_doi[0].text

    date = ''
    for tag in xml_doc.iter('year'):
        date = tag.text
        break
    for tag in xml_doc.iter('month'):
        try:
            if len(tag.text) < 2:
                date = date + '-0' + tag.text
            else:
                date = date + '-' + tag.text
        except: #AttributeError:
            date = date + '-01'
        break
    if date != '':
        Date.append(date)
    else:
        Date.append(np.nan)
        #Extracts the journal name, always available
        journ = ''
        for tag in xml_doc.iter('journal-title'):
            journ = tag.text
        if journ != '' and journ != None:
            Journal.append(UN.unidecode(journ))
        else:
            Journal.append(np.nan)
        #Extracts the title of the paper, always available
        title = ''
        for tag in xml_doc.iter('title-group'):
            title = tag.find('article-title').text
        if title != '' and title != None:
            Title.append(UN.unidecode(title))
        else:
            Title.append(np.nan)
        #Extract the names of the Authors, always available
        author = []
        for tags in xml_doc.iter('contrib'):
                for tag in tags.iter('name'):
                    try:
                        full_name = tag.find('surname').text
                    except AttributeError:
                        pass
                    #Sometimes only the surname is given, nit the names
                    try:
                        full_name = full_name + ' ' + tag.find('given-names').text
                    except AttributeError:
                        pass
                    except TypeError:
                        pass
                    try:
                        author.append(UN.unidecode(full_name))
                    except AttributeError:
                        pass
        if len(author) != 0:
            Authors.append(";".join(author))
        else:
            Authors.append(np.nan)
        #Extracts the corresponding affiliations (itertext takes all text between the aff tags
        #   so we need to remove the first character which is number), not always available
        affiliation = []
        for tag in xml_doc.iter('aff'):
            try:
                affiliation.append(UN.unidecode("".join(tag.itertext())[0:]))
            except AttributeError:
                pass
        if len(affiliation) !=0:
            Aff.append(";".join(affiliation))
        else:
            Aff.append(np.nan)
        #Extracts the full abstract (itertext takes all text between the abstract tags, so we
        #   remove all \n characters and all superfluous spaces), not always available
        abstract = ''
        for tag in xml_doc.iter('abstract'):
            abstract= "".join(tag.itertext()).replace('\n','')
        if abstract != '' and abstract != None:
            Abs.append(UN.unidecode(" ".join(abstract.split())))
        else:
            Abs.append(np.nan)
        #Extracts the MeshKeywords, not always available
        keywords=[]
        for tag in xml_doc.iter('kwd'):
            try:
                keywords.append(UN.unidecode(tag.text))
            except AttributeError:
                pass
        if len(keywords) != 0:
            MesH.append(";".join(keywords))
        else:
            MesH.append(np.nan)
        #Extracts the full text, not always available
        full_text = ''
        for tag in xml_doc.iter('body'):           
            full_text = "".join(tag.itertext()).replace('\n','')
        if full_text != '' and full_text != None:
            FullT.append(UN.unidecode(" ".join(full_text.split())))
            URL.append(np.nan)
        else:
            #Extracts the full text, not available by default (PubMed)
            #   so fetching URL from DOI, then downloading cooresponding PDF and
            #   extracting the text
            doi_missing = DOI[PMC_ID.index(ID)]
            if not pd.isnull(doi_missing):
                #Creating file name for PDF
                file_name = doi_missing.replace('.', '_').replace('/', '_').replace('-', '_')
                #Getting the URL from the DOI
                url_PDF = get_URL_from_DOI(doi_missing)
                #If the URL is present
                if not pd.isnull(url_PDF):
                    URL.append(url_PDF)
                    status, file_size = download_from_URL(url_PDF, './DownloadedPDF/' + name + '/', file_name)
                    #We have an actual file, so we store it, otherwise, do nothing
                    if (file_size > 0):
                        FullT.append(convert_PDF(file_name, name))
                    else:
                        FullT.append(np.nan)
                #Else we didn't find the PDF, no full text
                else:
                    URL.append(np.nan)
                    FullT.append(np.nan)
            #No DOI, no URL => no full text
            else:
                URL.append(np.nan)
                FullT.append(np.nan)

#            FullT.append(np.nan)

        if dump_in >= int(50):
            print ("Dumping some data")
            #DUmps some data to not have to start at beginning if a problem occurs
            dict = {'Date':Date, 'DOI':DOI_Fetched, 'PMCID':Fetched, 'PMID':PMID_Fetched, 'Journal':Journal, \
                'Title':Title, 'Authors':Authors, 'Affiliation':Aff, \
                'Abstract':Abs, 'Keywords': MesH, 'Full text':FullT, 'URL':URL}

            dataFrame = pd.DataFrame(dict)
            #Exports to DB for later use
            dataFrame.to_sql(db, engine, if_exists='append', chunksize = 50)
            #Resets entries
            Date, Journal, Title, Authors, Aff, Abs, MesH,FullT = [],[], [], [], [], [], [], []
            Fetched, DOI_Fetched, PMID_Fetched = [], [], []
            URL = []
            dump_in = 0

    #creates a dictionnary and forms a pandas DataFrame for easier data
    #   analysis later
    dict = {'Date':Date, 'DOI':DOI_Fetched, 'PMCID':Fetched, 'PMID':PMID_Fetched, 'Journal':Journal, \
            'Title':Title, 'Authors':Authors, 'Affiliation':Aff, \
            'Abstract':Abs, 'Keywords': MesH, 'Full text':FullT, 'URL': URL}

    #creates or append to the previous dataFrame
    dataFrame = pd.DataFrame(dict)
    #Exports to DB for later use
    dataFrame.to_sql(db, engine, if_exists='append', chunksize = 50)
    print ('Data acquired from the database')

    



def get_article_parallel(research,ID_list):
    pass

def Get_PMC(email, tool, search_term, name):
    #Sets database name for pmc

    #sets the location of the API for the query
    api_query = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'

    #sets the location of the API for the fetching (PMC only?)
    api_fetch = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'

    #creates the query to the DB to get the number of papers matching the
    #   search_term:    
    #   1)Creates the base query
    #   2)Parses the xml response to get the total number of pages and papers
    query_base = api_query + 'db=' + db.lower() + '&term=' + search_term
    print ('Sending request for ' + query_base)

    #gets the XML response
    xml_doc = ET.parse(urlopen(query_base)).getroot()

    #gets the content of the tag Count (number of papers)   
    max_pages = int(xml_doc.find('Count').text)

    #Populates the PMC_ID list by either None or with the values from the
    #   previous data
    if engine.dialect.has_table(engine, db):
        PMC_ID_i = dataFrame_previous['PMCID'].tolist()
        PMC_ID_i = [str(x) for x in PMC_ID_i]
    else:
        PMC_ID_i = []
    PMC_ID = []

    #by default, a query to the DB returns 20 results, so we adapt
    #   the query based on the number of total papers found by
    #   the basic search, so that instead of making total/20 queries,
    #   we just make 2 (gain of time of factor 60)!
    query = query_base + '&RetMax=' + str(max_pages)
    #all IDs are stored in the XML response of query, we parse the XML
    #   extract the PMCID from the it, and add it to a ID_list
    xml_doc = ET.parse(urlopen(query)).getroot()
    for ID in xml_doc.iter('Id'):
        #if the ID is not in the list already, then we add it to the list
        if ID.text not in PMC_ID_i:
            PMC_ID.append(ID.text)

    #Checks if there was more entries than previously. If not, then does nothing
    if engine.dialect.has_table(engine, db):
        if len(PMC_ID) == 0:
            #print (dataFrame_previous.info())
            print ('No new entry from PMC')
            return
        else:
            print ('There are %s new entries' % str(len(PMC_ID)))

    #for all extracted IDs
    #   1 - Extracts the corresponding PMID and DOIs
    print ('Getting PMIDs and DOIs')
    PMID = []
    DOI = []
    
    for i in range(len(PMC_ID)):
        ID_List = str(PMC_ID[i])
        url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/idconv.fcgi?ids=' +\
              ID_List +'&idtype=pmcid&format=json&versions=no&showaiid=no&tool='+ tool +\
              '&email=' + email
        #Gets the JSON response
        try:
            json_data = requests.get(url).json()
            #Extracts PMID and DOI for each entry
            for ID in json_data['records']:
                if 'pmid' in ID:
                    PMID.append(ID['pmid'])
                else:
                    PMID.append(np.nan)
                if 'doi' in ID:
                    DOI.append(ID['doi'])
                else:
                    DOI.append(np.nan)
        except:
            print('Data could not get fetched')
            PMID.append(np.nan)
            DOI.append(np.nan)
            
        

    #   2 - Extracts the remaining information
    print ('Extracting the data for the set of the request')
    Date, Journal, Title, Authors, Aff, Abs, MesH,FullT = [],[], [], [], [], [], [], []
    Fetched, DOI_Fetched, PMID_Fetched = [], [], []
    URL = []
    dump_in = 0
    for ID in PMC_ID:
        print ('Fetching ID', ID)
        fetch = api_fetch + 'db=pmc' + '&id=' + ID + '&tool=' + tool + \
                '&email=' + email
        
        dump_in = dump_in + 1
        Fetched.append(ID)
        DOI_Fetched.append(DOI[PMC_ID.index(ID)])
        PMID_Fetched.append(PMID[PMC_ID.index(ID)])
        try:
            xml_doc = ET.parse(urlopen(fetch)).getroot()
        except:
            xml_doc = ET.fromstring("<root>blabla</root>")
            
        #Removes all unnecessary data (Tables, captions and figure related tags)
        ET.strip_elements(xml_doc, 'xref','table-wrap','fig', with_tail=False)
        #Extracts the date from the XML, always available
        date = ''
        for tag in xml_doc.iter('year'):
            date = tag.text
            break
        for tag in xml_doc.iter('month'):
            try:
                if len(tag.text) < 2:
                    date = date + '-0' + tag.text
                else:
                    date = date + '-' + tag.text
            except: #AttributeError:
                date = date + '-01'
            break
        if date != '':
            Date.append(date)
        else:
            Date.append(np.nan)
        #Extracts the journal name, always available
        journ = ''
        for tag in xml_doc.iter('journal-title'):
            journ = tag.text
        if journ != '' and journ != None:
            Journal.append(UN.unidecode(journ))
        else:
            Journal.append(np.nan)
        #Extracts the title of the paper, always available
        title = ''
        for tag in xml_doc.iter('title-group'):
            title = tag.find('article-title').text
        if title != '' and title != None:
            Title.append(UN.unidecode(title))
        else:
            Title.append(np.nan)
        #Extract the names of the Authors, always available
        author = []
        for tags in xml_doc.iter('contrib'):
                for tag in tags.iter('name'):
                    try:
                        full_name = tag.find('surname').text
                    except AttributeError:
                        pass
                    #Sometimes only the surname is given, nit the names
                    try:
                        full_name = full_name + ' ' + tag.find('given-names').text
                    except AttributeError:
                        pass
                    except TypeError:
                        pass
                    try:
                        author.append(UN.unidecode(full_name))
                    except AttributeError:
                        pass
        if len(author) != 0:
            Authors.append(";".join(author))
        else:
            Authors.append(np.nan)
        #Extracts the corresponding affiliations (itertext takes all text between the aff tags
        #   so we need to remove the first character which is number), not always available
        affiliation = []
        for tag in xml_doc.iter('aff'):
            try:
                affiliation.append(UN.unidecode("".join(tag.itertext())[0:]))
            except AttributeError:
                pass
        if len(affiliation) !=0:
            Aff.append(";".join(affiliation))
        else:
            Aff.append(np.nan)
        #Extracts the full abstract (itertext takes all text between the abstract tags, so we
        #   remove all \n characters and all superfluous spaces), not always available
        abstract = ''
        for tag in xml_doc.iter('abstract'):
            abstract= "".join(tag.itertext()).replace('\n','')
        if abstract != '' and abstract != None:
            Abs.append(UN.unidecode(" ".join(abstract.split())))
        else:
            Abs.append(np.nan)
        #Extracts the MeshKeywords, not always available
        keywords=[]
        for tag in xml_doc.iter('kwd'):
            try:
                keywords.append(UN.unidecode(tag.text))
            except AttributeError:
                pass
        if len(keywords) != 0:
            MesH.append(";".join(keywords))
        else:
            MesH.append(np.nan)
        #Extracts the full text, not always available
        full_text = ''
        for tag in xml_doc.iter('body'):           
            full_text = "".join(tag.itertext()).replace('\n','')
        if full_text != '' and full_text != None:
            FullT.append(UN.unidecode(" ".join(full_text.split())))
            URL.append(np.nan)
        else:
            #Extracts the full text, not available by default (PubMed)
            #   so fetching URL from DOI, then downloading cooresponding PDF and
            #   extracting the text
            doi_missing = DOI[PMC_ID.index(ID)]
            if not pd.isnull(doi_missing):
                #Creating file name for PDF
                file_name = doi_missing.replace('.', '_').replace('/', '_').replace('-', '_')
                #Getting the URL from the DOI
                url_PDF = get_URL_from_DOI(doi_missing)
                #If the URL is present
                if not pd.isnull(url_PDF):
                    URL.append(url_PDF)
                    status, file_size = download_from_URL(url_PDF, './DownloadedPDF/' + name + '/', file_name)
                    #We have an actual file, so we store it, otherwise, do nothing
                    if (file_size > 0):
                        FullT.append(convert_PDF(file_name, name))
                    else:
                        FullT.append(np.nan)
                #Else we didn't find the PDF, no full text
                else:
                    URL.append(np.nan)
                    FullT.append(np.nan)
            #No DOI, no URL => no full text
            else:
                URL.append(np.nan)
                FullT.append(np.nan)

#            FullT.append(np.nan)

        if dump_in >= int(50):
            print ("Dumping some data")
            #DUmps some data to not have to start at beginning if a problem occurs
            dict = {'Date':Date, 'DOI':DOI_Fetched, 'PMCID':Fetched, 'PMID':PMID_Fetched, 'Journal':Journal, \
                'Title':Title, 'Authors':Authors, 'Affiliation':Aff, \
                'Abstract':Abs, 'Keywords': MesH, 'Full text':FullT, 'URL':URL}

            dataFrame = pd.DataFrame(dict)
            #Exports to DB for later use
            dataFrame.to_sql(db, engine, if_exists='append', chunksize = 50)
            #Resets entries
            Date, Journal, Title, Authors, Aff, Abs, MesH,FullT = [],[], [], [], [], [], [], []
            Fetched, DOI_Fetched, PMID_Fetched = [], [], []
            URL = []
            dump_in = 0

    #creates a dictionnary and forms a pandas DataFrame for easier data
    #   analysis later
    dict = {'Date':Date, 'DOI':DOI_Fetched, 'PMCID':Fetched, 'PMID':PMID_Fetched, 'Journal':Journal, \
            'Title':Title, 'Authors':Authors, 'Affiliation':Aff, \
            'Abstract':Abs, 'Keywords': MesH, 'Full text':FullT, 'URL': URL}

    #creates or append to the previous dataFrame
    dataFrame = pd.DataFrame(dict)
    #Exports to DB for later use
    dataFrame.to_sql(db, engine, if_exists='append', chunksize = 50)
    print ('Data acquired from the database')

    return
