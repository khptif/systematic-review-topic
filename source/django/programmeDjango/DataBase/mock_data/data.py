import csv
import sys
import nltk
from nltk.corpus import wordnet as wn
import re

# we extract article from csv file
file_article = open("DataBase/mock_data/df_sample.csv")
csv.field_size_limit(sys.maxsize)
csvreader = csv.reader(file_article)

articles = []
limit = 1000
i = 0
for row in csvreader:
    articles.append(row)
    limit += 1
    if i > limit:
        break

file_article.close()

# we define a list of all noun in english language
nltk.download('wordnet')
nltk.download('omw-1.4')
single_keywords = []
l = 0
for word in list(wn.all_synsets(wn.NOUN)):
    w = str(word.lemmas()[0].name())
    # we filter noun with '_' caracter
    if re.findall("[_]+",w) :
        continue
    else:
        single_keywords.append(w)




    
