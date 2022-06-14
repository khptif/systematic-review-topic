import re
from DataBase.models import *
from UI_Front.functions.utils_functions import *
from django.db.models import Q


def filter_recover_data(post_data):
    """ if we cancel and return to the page of selection with all filter.We recuperate data so we can write them in the html page
        input : dictionnary with key in format= "filter_X_Y" X is the numero of the filter and Y the numero of element in the filter
            value is a string. The format of each string is
            "Type:data_type;name_value:value;"
            for data_type = topic -> "Type:topic;topic_name:name_of_topic" name of topic is in format [A-Za-z0-9_,\-\s]+ .
            for data_type = author -> "Type:author;name:name;" name format is [A-Za-z0-9\-\s_]. It can be without name
            for data_type = keyword -> "Type:keyword;keyword:value;" the value can be [A-Za-z0-9\-\s_]
            for data_type = neighbour -> "Type:neighbour;DOI:value;
            
        output : dictionnary of dictionnary. each dictionnary is a filter block and have the keys: 
                topic,author,keyword and doi. each of them is a list of value"""
    
    filters = dict()
    for key,value in post_data.items():

        # if this is a filter post data
        filter_name = re.findall("^filter_[0-9]+",key)
        if filter_name:
            filter_name = filter_name[0]
            # we check if this a filter we have already meet
            if not filter_name in filters:
                filters[filter_name]= dict()
            # we check the type of filter
            
            type = re.findall("^Type:[a-z]+",value)
            type = type[0].replace("Type:","")

            #we check all type
            if type=='topic':
                topic_name = re.findall("topic_name:[A-Za-z0-9_,\-\s]+",value)
                topic_name = topic_name[0].replace("topic_name:","")
                if not 'topic' in filters[filter_name]:
                    filters[filter_name]['topic'] = []

                filters[filter_name]['topic'].append(topic_name)
                
            elif type=='author':
                #we retrive last name and first name and check if they are correct or exist
                name = re.findall("name:[A-Za-z0-9\-\s_]+",value)
                if not name:
                    name = ""
                else:
                    name = name[0].replace("name:","")

                if not 'author' in filters[filter_name]:
                    filters[filter_name]['author'] =[]

                filters[filter_name]['author'].append(name)

            elif type=='keyword':
                keyword = re.findall("keyword:[A-Za-z0-9\-\s_]+",value)
                keyword = keyword[0].replace("keyword:","")

                if not 'keyword' in filters[filter_name]:
                    filters[filter_name]['keyword'] = []
                filters[filter_name]['keyword'].append(keyword)

            elif type=='neighbour':
                doi = re.findall("DOI:[A-Za-z0-9\-\s_\.\/]+",value)
                doi = doi[0].replace("DOI:","")

                if not 'doi' in filters[filter_name]:
                    filters[filter_name]['doi'] = []
                
                filters[filter_name]['doi'].append(doi)
            else:
                continue

    return filters



def filters_manager(research,post_data):
    """
    We first give the research object.
    We secondly give the dictionnary with post data and return a dictionnary:
    input:  dictionnary with key in format= "filter_X_Y" X is the numero of the filter and Y the numero of the element in the filter.
            value is a string. The format of each string is
            "Type:data_type;name_value:value;"
            for data_type = topic -> "Type:topic;topic_name:name_of_topic;" name of topic is in format [A-Za-z0-9_,\-\s]+ .
            for data_type = author -> "Type:author;name:name;" name format is [A-Za-z0-9\-\s_]. It can be without name
            for data_type = keyword -> "Type:keyword;keyword:value;" the value can be [A-Za-z0-9\-\s_]
            for data_type = neighbour -> "Type:neighbour;DOI:value;"

    output: dictionnary in this format
            dict["filter_[0-9]+"] . The key represent the name of a filter and the value is a dictionnary in this format:
                dict["type of value"] = list of these value.
                type of value = 'topic', value = ["topic1","topic2",etc...], topic name
                type of value = 'author', value = a list of the Author objects that name match with last_name and/or first_name match
                type of value = 'keyword', value = ["key1","key2",etc...]
                type of value = 'neighbour' value = [article_object that has the same doi in input]
    """

    filters = dict()
    for key,value in post_data.items():

        # if this is a filter post data
        filter_name = re.findall("^filter_[0-9]+",key)
        if filter_name:
            filter_name = filter_name[0]
            # we check if this a filter we have already meet
            if not filter_name in filters:
                filters[filter_name]= dict()

            # we check the type of filter
            type = re.findall("^Type:[a-z]+",value)
            type = type[0].replace("Type:","")

            if type=='topic':
                #if topic, we retrieve the topic name and append it to the return list
                topic_name = re.findall("topic_name:[A-Za-z0-9_,\-\s]+",value)
                topic_name = topic_name[0].replace("topic_name:","")

                #we check if we already have in the subdictionnary the key "topic". Otherwise, we initiate it with empty list
                if not 'topic' in filters[filter_name]:
                    filters[filter_name]['topic'] = []

                filters[filter_name]['topic'].append(topic_name)
                
            elif type=='author':
                #if author, we retrieve name given and check if there is a match in last name or first name.
                name = re.findall("name:[A-Za-z0-9\-\s_]+",value)
                if not name:
                    name = ""
                else:
                    name = name[0].replace("name:","")

                #we retrieve the author we check for last name and after the first_name
                #the match is not exact and not case sensitive.
                #Example: "Car" match with "carlos" or "carol". If last nam or first name have the pattern, it match.
                authors_list = []
                
                string_reg = r".*"+name+".*"
                authors_list = Author.objects.filter(Q(last_name__iregex=string_reg) | Q(first_name__iregex=string_reg)).order_by("last_name")
                
                #if doesn't exist, we continue on next iteration
                if not authors_list.exists():
                    continue
                
                #we check if we already have in the subdictionnary the key "author". Otherwise, we initiate it with empty list
                if not 'author' in filters[filter_name]:
                    filters[filter_name]['author'] =[]
                
                # as one name can be associate to many author, we send all match with authors
                for author in authors_list:
                    #we check if the author is already in the list
                    if author in filters[filter_name]['author']:
                        continue
                    filters[filter_name]['author'].append(author)

            elif type=='keyword':
                # we retrieve the keyword and append it
                keyword = re.findall("keyword:[A-Za-z0-9\-\s_]+",value)
                keyword = keyword[0].replace("keyword:","")

                #we check if we already have in the subdictionnary the key "keyword". Otherwise, we initiate it with empty list
                if not 'keyword' in filters[filter_name]:
                    filters[filter_name]['keyword'] = []
                filters[filter_name]['keyword'].append(keyword)

            elif type=='neighbour':
                # we retrieve the article with the doi if exists
                # we get the doi string
                doi = re.findall("DOI:.+",value)
                doi = doi[0].replace("DOI:","")
                doi = doi[0:-1] # we delete the ';' at end
                #we check if we already have in the subdictionnary the key "neighbour". Otherwise, we initiate it with empty list
                if not 'neighbour' in filters[filter_name]:
                    filters[filter_name]['neighbour'] = []
                
                #we check if the doi match with one of the article of the research
                article = Article.objects.filter(doi=doi,research_article__research=research)
                if article.exists():
                    filters[filter_name]['neighbour'].append(article[0])
            else:
                continue

    return filters


def get_Articles_Filtered(research,filters):
    """ The function take the research id and filters, build a list of article who match 
    the filters and return the list of the article id. If we choose id instead of the object,
    this is to save it in user session as a list of integer.
    
    input: dictionnary in this format
            dict["filter_[0-9]+"] . The key represent the name of a filter and the value is a dictionnary in this format:
                dict["type of value"] = list of these value.
                type of value = 'topic', value = ["topic1","topic2",etc...], topic name
                type of value = 'author', value = a list of the Author objects that last_name and/or first_name match
                type of value = 'keyword', value = ["key1","key2",etc...]
                type of value = 'neighbour' value = [article_object that has the same doi in input]

    output: list of objects of Article
    """

    return_article_list = []
    # we check in these order: topic,author,Doi and keyword
    # for all block filters. In a block, logical operation is AND

    for _ , filter in filters.items():
        
        #as the logical operation is AND, we define a first list of article
        # and we remove articles from this first list
        first = True
        article_list = []

        #if we detect an empty set of article, we continue on next block filter
        empty = False

        #we check topic filters
        if 'topic' in filter:
            for topic in filter['topic']:
                # we get all cluster object with the topic
                cluster_list = Cluster.objects.filter(topic=topic, research=research)
                # if this is the first filter in this block filter, the initial set of article
                # is the article where there is a match with the topic in cluster objects
                if first:
                    for cluster in cluster_list:
                        article_list.append(cluster.article)
                    first=False
                    continue
                
                next_list = []
                for cluster in cluster_list:
                    #we check if article exist already in current list
                    if cluster.article in article_list:
                        next_list.append(cluster.article)
                # no similar object => AND op give empty set
                if next_list == []:
                    empty = True
                    break
                else:
                    article_list = next_list
        if empty:
            empty=False
            continue
        
        #we check author filter
        if 'author' in filter:
            for author in filter['author']:
                
                article_author_list = []
                #we retrieve all article_author objects for all author in the research 
                a = Article_Author.objects.filter(author=author,article__research_article__research = research)

                for article_author in a:
                    article_author_list.append(article_author)
                    
                #if first, the initial article set is all article from article_author_list
                if first:
                    for article_author in article_author_list:
                        article_list.append(article_author.article)
                        first=False
                        continue
                
                next_list =[]
                #we check if article exist already in current list
                for article_author in article_author_list:
                    if article_author.article in article_list:
                        next_list.append(article_author.article)
                # no similar object => AND op give empty set
                if next_list == []:
                    empty = True
                    break
                else:
                    article_list = next_list
        if empty:
            empty = False
            continue
        
        #we check neighbour filter
        if 'neighbour' in filter:
            for article_center in filter['neighbour']:
                
                # we get nearest neighbour. By default, the fonction neighbour_article get 5 article
                neighbour_articles_list = neighbour_article(article=article_center,research=research)
                
                # if first, the initial list is composed from the nearest neighbour of the first article
                if first:
                    for article in neighbour_articles_list:
                        article_list.append(article)
                    first = False
                    continue
                next_list = []

                # we check if there are similar article
                for article in neighbour_articles_list:
                    if article in article_list:
                        next_list.append(article)
                # no similar object => AND op give empty set
                if next_list == []:
                    empty=True
                    break
                else:
                    article_list = next_list
        if empty:
            empty:False
            continue

        # We check keyword filter
        if 'keyword' in filter:
            for keyword in filter['keyword']:
                #if first, the initial set of article is all article in DataBase who have at least 1 match in his abstract firstly
                # and in his full_text secondly. the match is insensitive case
                if first:
                    regex_key = r".*" + keyword + r".*"
                    article_list = Article.objects.filter(research_article__research=research).filter(Q(abstract__iregex=regex_key) | Q(full_text__iregex=regex_key))
                    first = False
                    continue
                
                #we check in article set if there is a match in abstract firstly and fulltext secondly.
                #If not, the article is removed. If no article match, we have an empty set.
                next_list =[]
                for article in article_list:
                    # we check if there are match in abstract
                    match = re.findall(keyword, article.abstract,re.IGNORECASE)
                    if match :
                        next_list.append(article)
                        continue
                    # we check the full text 
                    match = re.findall(keyword,article.full_text,re.IGNORECASE)
                    if match :
                        next_list.append(article)
                        continue
                # no similar object => AND op give empty set
                if next_list == []:
                    empty=True
                    break
                else:
                    article_list = next_list
        if empty:
            empty = False
            continue
        # if the filter block get some articles, we append in the final set of article the articles's id.
        # we check if the article is already in the list
        for article in article_list:
            if article.id in return_article_list:
                continue
            return_article_list.append(article.id)
    
    return return_article_list    