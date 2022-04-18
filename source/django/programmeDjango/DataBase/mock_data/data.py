import csv
import sys
import re

# we extract article from csv file
file_article = open("DataBase/mock_data/df_sample.csv")
csv.field_size_limit(sys.maxsize)
csvreader = csv.reader(file_article)

articles = []
limit = 20000
i = 0
for row in csvreader:
    articles.append(row)
    limit += 1
    if i > limit:
        break

file_article.close()





    
