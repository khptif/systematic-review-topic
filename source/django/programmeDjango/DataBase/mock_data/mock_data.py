from DataBase.models import Article , Author, Article_Author
from DataBase.mock_data.data import articles
import re
import datetime
# we create the articles and their author in the database
# one row is (Title, PMCID, Authors, Abstract, Fulltext, URL, Year)
title = True
for article in articles:
    # the first row are titles
    if title:
        title=False
        continue
    title = article[0]
    
    doi = article[2]
    pmcid = article[3]
    abstract = article[5]
    fulltext = article[6]
    url = article[7]
    year = int(re.findall("[0-9]{4}",article[9])[0])

    article_object = Article.objects.create(title=title,pmcid=pmcid,abstract=abstract,full_text=fulltext,url_file=url,publication=datetime.date(year,1,1),doi=doi)

    #if there are no authors
    if not re.findall("[a-zA-Z\-]+",article[4]):
        continue
    authors = article[4].split(',')
    
    for author in authors:
        print(author)
        names = re.findall("[a-zA-Z\-]+",author)
        if not names:
            continue
        last_name = names[0]
        author = author.replace(last_name,"")
        first_name = author
        #we delete space in beginning and ending
        last_name = re.findall("[a-zA-z\-]{1}[a-zA-z\-\s]*[a-zA-Z\-]{1}",last_name)
        first_name = re.findall("[a-zA-z\-]{1}[a-zA-z\-\s]*[a-zA-Z\-]{1}",first_name)
        authors_object = Author.objects.create(last_name=last_name,first_name=first_name)
        Article_Author.objects.create(author=authors_object,article=article_object)
        