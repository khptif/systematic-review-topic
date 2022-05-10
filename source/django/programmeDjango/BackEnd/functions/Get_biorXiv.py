import sys, os, time
from urllib.request import urlopen
import requests
import json as JS
import pandas as pd
import numpy as np
import unidecode as UN
from bs4 import BeautifulSoup

import BackEnd.functions.PDF_download as pdf
import concurrent.futures


def extract_id(search_term):
    api_query = 'https://www.biorxiv.org/search/'
    query_base = api_query + search_term  
    
    id = []
    metadata ={}
    
    first_page_query = query_base
    text = requests.get(first_page_query).text
    soup = BeautifulSoup(text, 'html.parser')
    last_str = soup.select_one('li.pager-last.last.odd a').string
    print(last_str + " pages")    
    num_pages = int(last_str)

    for i in range(num_pages):

        query = query_base if i == 0 else query_base + '?page=' + str(i)
        text = requests.get(query).text
        soup = BeautifulSoup(text, 'html.parser')
        entries = soup.select('div.highwire-article-citation')

        for entry in entries:
            entry_id = entry['data-pisa']
            id.append(entry_id)
            metadata[entry_id] = entry

    return id,metadata


def extract_metadata(entry_id,entry):
    
    doi_url = str(entry[entry_id].select_one(".highwire-cite-metadata-doi").contents[1]).strip()
    doi = doi_url.replace("https://doi.org/", "")

    authors_str = ";".join(map(lambda x: x.text, entry[entry_id].select(".highwire-citation-author")))
    date_str = entry_id.replace("biorxiv;", "")[0:10]
    title_sel = entry[entry_id].select_one('.highwire-cite-linked-title')
    title_str = title_sel.text
    abstract_url = "https://www.biorxiv.org" + title_sel["href"]
    url = abstract_url + ".full.pdf"

    db_entry = {
        'Date': date_str,
        'Title': title_str,
        'Authors': authors_str,
        'Affiliation': None,
        'Abstract': None,
        'Keywords': None,
        'DOI': doi,
        'URL': url
    }

    abstract_page = requests.get(abstract_url).text
    soup = BeautifulSoup(abstract_page, 'html.parser')
    sel = soup.select_one('div#abstract-1 p').text
    db_entry['Abstract'] = sel

    return db_entry

def Get_biorXiv( search_term, name):
    
    id, entry = extract_id(search_term)

    print("number of article: " + str(len(id)))
    fichier = open("BackEnd/functions/results/"+name,"a")

    total = str(len(id))
    current = 0
    for i in id:

        print("\r"+str(current) + "/" + total, end='')
        metadata = extract_metadata(i,entry)
        fichier.write("Titre: " + metadata['Title'] + "\n")
        fichier.write("Authors: \n" + metadata["Authors"] + "\n")
        fichier.write("DOI: " + metadata["DOI"] + "\n")
        fichier.write("Abstract: " + metadata['Abstract'] + "\n")

        full_text = pdf.extract_full_text(metadata['URL'],"bio")
        fichier.write("Full text: " + str(full_text) + "\n")

        current += 1

    print()
    fichier.close()

    return

if __name__ == "__main__":
    search = sys.argv[1]
    name = sys.argv[2]
    Get_biorXiv(search,name)

