import re
from DataBase.models import *
from UI_Front.functions.utils_functions import *


def filters_manager(post_data):
    """ We give the dictionnary with post data and return a dictionnary:
        # filters[i] = one filter block
        # filters[i]['topic'] = list of topic, 
        # ['author'] = list of author, 
        # ['neighbour'] = list of article we want neighbour article,
        # ['keyword'] = list of keywords"""
    filters = dict()
    for key,value in post_data.items():
        filter_name = re.findall("^filter_[0-9]+",key)
        # if this is a filter post data
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
                topic_name = re.findall("topic_name:[A-Za-z0-9_\-\s]+",value)
                topic_name = topic_name[0].replace("topic_name:","")
                if not 'topic' in filters[filter_name]:
                    filters[filter_name]['topic'] = []
                filters[filter_name]['topic'].append(topic_name)
                
            elif type=='author':
                #we retrive last name and first name and check if they are correct or exist
                last_name = re.findall("last_name:[A-Za-z0-9\-\s_]+",value)
                if not last_name:
                    last_name = ""
                else:
                    last_name = last_name[0].replace("last_name:","")

                first_name = re.findall("first_name:[A-Za-z0-9\-\s_]+",value)
                if not first_name:
                    first_name =""
                else:
                    first_name = first_name[0].replace("first_name:","")
            
                #we retrieve the author
                authors_list = []
                if not first_name =="" and  last_name =="":
                    string_reg = r".*"+first_name+".*"
                    authors_list = Author.objects.filter(first_name__iregex=string_reg)
                elif  first_name =="" and not last_name =="":
                    string_reg = r".*"+last_name+".*"
                    authors_list = Author.objects.filter(last_name__iregex=string_reg)
                elif not first_name =="" and not last_name =="":
                    string_reg_l = r".*"+last_name+".*"
                    string_reg_f = r".*"+first_name+".*"
                    authors_list = Author.objects.filter(last_name__iregex=string_reg_l,first_name__iregex=string_reg_f)
                else:
                    continue
                

                #if doesn't exist, we continue on next iteration
                if not authors_list.exists():
                    continue

                if not 'author' in filters[filter_name]:
                    filters[filter_name]['author'] =[]
                
                # as one name can be associate to many author, we send all match with authors
                filters[filter_name]['author'].append(authors_list)

            elif type=='keyword':
                keyword = re.findall("keyword:[A-Za-z0-9\-\s_]+",value)
                keyword = keyword[0].replace("keyword:","")

                if not 'keyword' in filters[filter_name]:
                    filters[filter_name]['keyword'] = []
                filters[filter_name]['keyword'].append(keyword)

            elif type=='neighbour':
                doi = re.findall("DOI:[A-Za-z0-9\-\s_]+",value)
                doi = doi[0].replace("DOI:","")

                if not 'neighbour' in filters[filter_name]:
                    filters[filter_name]['neighbour'] = []
                filters[filter_name]['neighbour'].append(doi)
            
            else:
                continue

    return filters


def get_Articles_Filtered(research,filters):
    """ The function take the research id and filters, build a list of article who match 
    the filters and return the list of the article id. If we choose id instead of the object,
    this is to save it in user session as a list of integer.
    The filters format is a dict() where each element is a block of filters. 
    This block is a dict() with ['topic'] a list of topic, ['author'] a list of list of author,
    ['neigbour'] a list of article's DOI, ['keyword'] a list of keyword."""

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
            for author_list in filter['author']:
                
                article_author_list = []
                #we retrieve all article_author objects for all author in the research 
                for author in author_list:
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
            for doi in filter['neighbour']:
                #we retrieve the article. If doesn't exist, it give us an empty set and we continue to next block filter
                string_reg = r".*" + doi + r".*"
                article_center = Article.objects.filter(doi__iregex=string_reg, research=research)
                if not article_center.exists():
                    empty = True
                    break
                # we get nearest neighbour. By default, the fonction neighbour_article get 5 article
                
                article_center = article_center[0]
                neighbour_articles_list = neighbour_article(article=article_center,research=research)
                
                # if first, the initial list is composed from the nearest neighbour of the first article
                if first:
                    for article in neighbour_articles_list:
                        article_list.append(article)
                    first = False
                    continue
                next_list = []

                # we check if there ar similar article
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
                    article_list = Article.objects.filter(research_article__research=research).filter(Q(abstract__icontains=keyword) | Q(full_text__icontains=keyword))
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