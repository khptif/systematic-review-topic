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