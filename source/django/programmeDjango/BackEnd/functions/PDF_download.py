#################################################################################################################################################
#                                                              IMPORT PACKAGES                                                                  #
#################################################################################################################################################

import os
#unidecode to remove accents and such
import unidecode as UN
#Pandas & numpy
import pandas as pd
import numpy as np
#This is to decode an URL whch contains % strings
import urllib.parse
from bs4 import BeautifulSoup
import requests

import PyPDF2
import urllib.request
from programmeDjango.settings import TEMPORARY_DATA

#session = FuturesSession()

#################################################################################################################################################
#                                                          SUBROUTINES                                                                          #
#################################################################################################################################################
def remove_char(string):
    '''
    Description
    --------------
    This function removes unwanted characters

    Takes
    --------------
    string (string)
    
    Returns
    --------------
    
    '''
    string = string.replace('\n',' ')
    return ''.join(e for e in string if (e.isalpha() or e.isspace() or e == '-' or e == "'"))


def download_from_URL(url,path_file):
    '''
    Description
    --------------
    This function downloads PDF from a direct URL

    Takes
    --------------
    url (string): URL to the PDF file
    output_path (string): where to store the PDF
    file_name (string): what will be the file name in the output_path.

    Returns
    --------------
    str status (string): status code of the requests
    file_size (int): size in bytes of the downloaded file
    '''
    try:
        response = urllib.request.urlopen(url)    
    except:
        print("error url pdf: " + url)
        return False
    
    

    try:
        file = open(path_file, 'wb')
        file.write(response.read())
        file.close()
    except:
        print("error in file pdf")
        return False

    return True

def convert_PDF(path_file):
    """
    Description
    --------------
    This function converts PDF to text to do text processing

    Takes
    --------------
    path_file (string): path to the pdf file. 
    
    Returns
    --------------
    text (string): the text conversion of the pdf
    """
    #create file object variable
    #opening method will be rb
    #if file doesn't exist, return False
    try:

        pdffileobj=open(path_file,'rb')
    except:
        return False
 
    #create reader variable that will read the pdffileobj
    try:
        pdfreader=PyPDF2.PdfFileReader(pdffileobj)
        num_page = pdfreader.numPages
    except:
        return False
        
    #This will store the number of pages of this pdf file
    
    final_text = ''
    
    for page in range(num_page):
        #create a variable that will select the selected number of pages
        pageobj=pdfreader.getPage(page)
 
        #create text variable which will store all text datafrom pdf file
        text=pageobj.extractText()

        # we append the text
        final_text += text + " "
    
    # we close the pdf file
    pdffileobj.close()

    # we return the final text
    return final_text 

def extract_full_text(url_PDF,name):
    """Extracts the full text. downloading cooresponding PDF from url and
       extracting the text. Return full_text pdf or nan if problem occurs"""
    
    path_pdf = TEMPORARY_DATA+ "/" + str(name) +".pdf"

    if download_from_URL(url_PDF,path_pdf) :
        
        full_text = convert_PDF(path_pdf)
        os.remove(path_pdf)
        return full_text

    else: #(the link to pdf or downloading was not working for some reason)
        return np.nan




def get_URL_from_DOI(doi):
    '''
    Description
    --------------
    This function gets a direct URL to a pdf based on DOI

    Takes
    --------------
    DOI (string): URL to the PDF file
    
    Returns
    --------------
    url_PDF (string/None): URL to the PDF file
    '''
    #Defines header to not be rejected
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    #Defines redirection terms (esp. for Elsevier)
    redirections = ['Redirecting', 'redirecting', 'Redirect', 'redirect', 'tag_url']
    #Constructs URL for DOI.org
    url_PDF = None
    url_DOI = 'https://doi.org/' + doi
    try:
        #Send the requests to DOI.org and parses th html response
        response = requests.get(url_DOI, headers = headers)
        url_base = response.url
        html = BeautifulSoup(response.text, features = 'lxml')
        #Check the title
        title = html.title.text
        #if this is a redirecting page, the title should mention it, so we need to access the actual page
        while (title in redirections):
            for link in html.find_all('meta'):
                url_DOI = str(link.get('content'))
                for redirection in redirections:
                    if (redirection in url_DOI):
                        #Gets the actual web page, sends a new request and parses it
                        url_DOI = url_DOI.split(redirection + '=')[-1]
                        if redirection == 'tag_url':
                            url_DOI = url_DOI.split('&title=')[0]
                        url_DOI = urllib.parse.unquote(url_DOI)
                        response = requests.get(url_DOI, headers = headers)
                        url_base = response.url
                        html = BeautifulSoup(response.text, features = 'lxml')
                        #Check the title
                        title = html.title.text
        #Gets the root access of the 
        url_base = url_base.split('/')[0] + '//' + url_base.split('/')[2]
        url_base_noHTTP = url_base.split('/')[2] 
        #Looks for tags with links
        #Checks if there's a link with a pdf file and the doi
        if 'sciencedirect' in url_base: #Elsevier
            url_PDF = 'http://api.elsevier.com/content/article/doi:' + doi + '?view=FULL'
            return url_PDF
        
        for link in html.find_all('meta'):
            current_link = str(link.get('content'))
            #skip adverts and doi.org links
            if ('pubads' in current_link) or ('doi.org' in current_link):
                continue
            if (doi in current_link) and ('file' in current_link):
                if not ((url_base_noHTTP in current_link) or ('http' in current_link)):
                    url_PDF = url_base + current_link
                else:
                    url_PDF = current_link
        #Wasn't a "meta" tag
        if pd.isnull(url_PDF): 
            for link in html.find_all('a'):
                current_link = str(link.get('href'))
                #skip adverts and doi.org links
                if ('pubads' in current_link) or ('doi.org' in current_link):
                    continue
                if (doi in current_link):
                    if not ((url_base_noHTTP in current_link) or ('http' in current_link)):
                        url_PDF = url_base + current_link
                    else:
                        url_PDF = current_link
                    break
                elif ('.pdf' in current_link) and ('doi' in current_link):
                    if not ((url_base_noHTTP in current_link) or ('http' in current_link)):
                        url_PDF = url_base + current_link
                    else:
                        url_PDF = current_link
                elif ('.pdf' in current_link):
                    if not ((url_base_noHTTP in current_link) or ('http' in current_link)):
                        url_PDF = url_base + current_link
                    else:
                        url_PDF = current_link
        #Wasn't a "meta" or "a" tag
        if pd.isnull(url_PDF): 
            for link in html.find_all('link'):
                current_link = str(link.get('href'))
                #skip adverts and doi.org links
                if ('pubads' in current_link) or ('doi.org' in current_link):
                    continue
                if ('.pdf' in current_link):
                    if not ((url_base_noHTTP in current_link) or ('http' in current_link)):
                        url_PDF = url_base + current_link
                    else:
                        url_PDF = current_link           
        #Tests if the site exists
        if not pd.isnull(url_PDF):
            #SOmetimes, just the http is missing
            if not ('http' in url_PDF):
                url_PDF = 'http:' + url_PDF
            print(url_PDF)
            test_url = requests.get(url_PDF, headers=headers).status_code
            if test_url != 200:
                url_PDF = None
                print('No response from the site. Error:', test_url)
                print('Could not get link from DOI', doi)
    except Exception as e:
        print(e)
        print('Could not get link from DOI', doi, url_PDF)
    if pd.isnull(url_PDF):
        return
    else:
        #Replace all possible '%XXX' codes that might be here
        return(urllib.parse.unquote(url_PDF))