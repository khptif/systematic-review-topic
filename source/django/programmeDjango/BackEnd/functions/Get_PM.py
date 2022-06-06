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
#PDF processing
from PDF_download import *
import concurrent.futures

def get_search_term(search):
    pass

def get_max_article(search):
    pass

def get_ID(search):
    pass

# sets the location of the API for the query
api_query = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'
# sets the location of the API for the fetching. Careful not responding with XML or JSON
api_fetch = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'

def download_one(ID, DOI, PMID, PMC_ID, tool, email, name):
    print('Fetching ID', ID)
    fetch = api_fetch + 'db=pubmed' + '&id=' + ID + '&tool=' + tool + \
            '&email=' + email + '&format=xml'

    # dict = {'Date':Date, 'DOI':DOI_Fetched, 'PMCID':PMC_ID_Fetched, 'PMID':Fetched, 'Journal':Journal, \
    #         'Title':Title, 'Authors':Authors, 'Affiliation':Aff, \
    #         'Abstract':Abs, 'Keywords': MesH, 'Full text':FullT, 'URL': URL}

    db_entry = {
        'PMID': ID,
        'DOI': DOI[PMID.index(ID)],
        'PMCID': PMC_ID[PMID.index(ID)]
    }

    try:
        xml_doc = ET.parse(urlopen(fetch)).getroot()
    except:
        xml_doc = ET.fromstring("<root>blabla</root>")

    # Extracts the date from the XML, always available
    date = ''
    for tag in xml_doc.findall('.//ArticleDate/Year'):
        date = tag.text
    for tag in xml_doc.findall('.//ArticleDate/Month'):
        try:
            if len(tag.text) < 2:
                date = date + '-0' + tag.text
            else:
                date = date + '-' + tag.text
        except:  # AttributeError:
            date = date + '-01'
    if date != '':
        db_entry.update(Date=date)
    else:
        db_entry.update(Date=np.nan)
    # Extracts the journal name, always available
    journ = ''
    for tag in xml_doc.findall('.//Journal/Title'):
        journ = tag.text.split(' : ')[0]
    if journ != '' and journ != None:
        db_entry.update(Journal=UN.unidecode(journ))
    else:
        db_entry.update(Journal=np.nan)
    # Extracts the title of the paper, always available
    title = ''
    for tag in xml_doc.findall('.//Article/ArticleTitle'):
        title = tag.text
    if title != '' and title != None:
        db_entry.update(Title=UN.unidecode(title))
    else:
        db_entry.update(Title=np.nan)
    # Extract the names of the Authors, not always available
    author = []
    for tag in xml_doc.findall('.//Author'):
        full_name = ''
        try:
            full_name = tag.find('LastName').text
            # Sometimes only the surname is given, nit the names
            try:
                full_name = full_name + ' ' + tag.find('ForeName').text
            except AttributeError:
                pass
            except TypeError:
                pass
        except AttributeError:
            pass
        author.append(UN.unidecode(full_name))
    if len(author) != 0:
        db_entry.update(Authors=";".join(author))
    else:
        db_entry.update(Authors=np.nan)
    # Extracts the corresponding affiliations (itertext takes all text between the aff tags
    #   so we need to remove the first character which is number), not always available
    affiliation = []
    for tag in xml_doc.findall('.//Affiliation'):
        temp = tag.text.split(';')
        for item in temp:
            if item not in affiliation:
                try:
                    affiliation.append(UN.unidecode(item))
                except AttributeError:
                    pass
    if len(affiliation) != 0:
        db_entry.update(Affiliation=";".join(affiliation))
    else:
        db_entry.update(Affiliation=np.nan)
    # Extracts the full abstract (itertext takes all text between the abstract tags, so we
    #   remove all \n characters and all superfluous spaces), not always available
    abstract = ''
    for tag in xml_doc.findall('.//AbstractText'):
        abstract = abstract + " " + "".join(tag.itertext()).replace('\n', '')
    if abstract != '' and abstract != None:
        db_entry.update(Abstract=UN.unidecode(" ".join(abstract.split())))
    else:
        db_entry.update(Abstract=np.nan)
    # Extracts the MeshKeywords, not always available
    keywords = []
    for tag in xml_doc.findall('.//Keyword'):
        try:
            keywords.append(UN.unidecode(tag.text))
        except AttributeError:
            pass
    if len(keywords) != 0:
        db_entry.update(Keywords=";".join(keywords))
    else:
        db_entry.update(Keywords=np.nan)
    # Extracts the full text, not available by default (PubMed)
    #   so fetching URL from DOI, then downloading cooresponding PDF and
    #   extracting the text
    doi_missing = DOI[PMID.index(ID)]
    if not pd.isnull(doi_missing):
        # Creating file name for PDF
        file_name = doi_missing.replace('.', '_').replace('/', '_').replace('-', '_')
        # Getting the URL from the DOI
        url_PDF = get_URL_from_DOI(doi_missing)
        # If the URL is present
        if not pd.isnull(url_PDF):
            db_entry.update(URL=url_PDF)
            status, file_size = download_from_URL(url_PDF, './DownloadedPDF/' + name + '/', file_name)
            return db_entry, status, file_size, file_name
        else:
            return db_entry, 404, 0, file_name
    else:
        return db_entry, 404, 0, 'none.pdf'

def Get_PM(email, tool, search_term, name):
    #Sets database name for pubmed
    engine = create_engine('sqlite:///DB/papers_DB_'+ name + '.db')
    db = 'PM'
    #previous_call = './' + tool + '_' + name + '_' + db + '.csv'
    db_entry = {}
    #Checks if the process has already been done for some papers in prevous search
    #   if that is the case, stores in a dataFrame
    if engine.dialect.has_table(engine, db):
        print ('Reading the previous call')
        query = 'SELECT * FROM '+ db +';'
        dataFrame_previous = pd.read_sql(query, engine)
        #dataFrame_previous = pd.read_csv(previous_call, index_col = 0)

    #creates the query to the DB to get the number of papers matching the
    #   search_term:
    #   1)Creates the base query
    #   2)Parses the xml response to get the total number of pages and papers
    query_base = api_query + 'db=pubmed&term=' + search_term
    print ('Sending request for ' + query_base)

    #gets the XML response
    xml_doc = ET.parse(urlopen(query_base)).getroot()

    #gets the content of the tag Count (number of papers)
    max_pages = int(xml_doc.find('Count').text)

    #Populates the PMID list by either None or with the values from the
    #   previous data
    if engine.dialect.has_table(engine, db):
        PMID_i = dataFrame_previous['PMID'].tolist()
        PMID_i = [ str(x) for x in PMID_i ]
    else:
        PMID_i = []
    PMID = []
    
    #by default, a query to the DB returns 20 results, so we adapt
    #   the query based on the number of total papers found by
    #   the basic search, so that instead of making total/20 queries,
    #   we just make 2 (gain of time of factor 60)!
    query = query_base + '&RetMax=' + str(max_pages)

    #all IDs are stored in the XML response of query, we parse the XML
    #   extract the PMID from the it, and add it to a ID_list
    xml_doc = ET.parse(urlopen(query)).getroot()
    for ID in xml_doc.iter('Id'):
        #if the ID is not in the list already, then we add it to the list
        if ID.text not in PMID_i:
            PMID.append(ID.text)
            
    #Checks if there was more entry than previously
    if engine.dialect.has_table(engine, db):
        if len(PMID) == 0:
            #print (dataFrame_previous.info())
            print ('No new entry from PubMed')
            return
        else:
            print ('There are %s new entries' % str(len(PMID)))

    #for all extracted IDs
    #   1 - Extracts the corresponding PMCID and DOIs
    print ('Getting PMCIDs and DOIs, total: {}'.format(len(PMID)))
    PMC_ID = []
    DOI = []

    for i in range(len(PMID)):
        ID_List = str(PMID[i])
        url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/idconv.fcgi?ids=' +\
              ID_List +'&idtype=pmid&format=json&versions=no&showaiid=no&tool='+ tool +\
              '&email=' + email
        try:
            #Gets the JSON response
            json_data = requests.get(url).json()
            #Extracts PMCID and DOI for each entry
            for ID in json_data['records']:
                if 'pmcid' in ID:
                    PMC_ID.append(ID['pmcid'])
                else:
                    PMC_ID.append(np.nan)
                if 'doi' in ID:
                    DOI.append(ID['doi'])
                else:
                    DOI.append(np.nan)
        except:
            #No respoonse
            PMC_ID.append(np.nan)
            DOI.append(np.nan)
            
    #2 - Extracts the rest of the information
    # Date, Journal, Title, Authors, Aff, Abs, MesH,FullT = \
    #                         [],[], [], [], [], [], [], []
    # Fetched, DOI_Fetched, PMC_ID_Fetched = [], [], []
    # URL = []
    dump_in = 0
    print('Extracting the data for the set of the request')
    futures = []
    data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for ID in PMID:
            future = executor.submit(download_one, ID, DOI, PMID, PMC_ID, tool, email, name)
            futures.append(future)

        dump_in = 0
        for future in concurrent.futures.as_completed(futures, 60):
            db_entry, status, file_size, file_name = future.result()
            if file_size > 0:
                print('Converting PDF: {}'.format(file_name))
                db_entry['Full text'] = convert_PDF(file_name, name)
            else:
                db_entry['Full text'] = np.nan
            data.append(db_entry)
            dump_in += 1
            if dump_in >= int(5):
                print("Dumping some data")
                # DUmps some data to not have to start at beginning if a problem occurs
                dataframe = pd.DataFrame(data)
                # Exports to DB for later use
                dataframe.to_sql(db, engine, if_exists='append', chunksize=50)
                # Resets entries
                data = []
                dump_in = 0

        dataframe = pd.DataFrame(data)
        dataframe.to_sql(db, engine, if_exists='append', chunksize=50)
        print('Data acquired from the database')


    return
