import random
import re
from django.db.models import Q
from UI_Front.forms import *
from UI_Front.models import *
from DataBase.models import *


def word_list(string_to_parse):
    """ From a search string, extract all keywords and return them"""
   
    lower_string = string_to_parse.lower()
    # we recuperate word in double quotes
    quotes_word = re.findall("\"[a-z0-9\-\s]+\"", lower_string)
    # we delete the multiple words from the string search
    for qw in quotes_word:
        lower_string = lower_string.replace(qw,"")

    # extract single words
    single_word = re.findall("([a-z0-9\-]+)",lower_string)
    return_list = []
    #build the return list of keywords
    for word in single_word:
        return_list.append(word)
    for word in quotes_word:
        return_list.append(word)

    return return_list

def sort_historical(research_list,sort_type):
    """ take a dictionnary key: id of research, value: list of Keywords objects. Return a list sorted 
    in this format: [(id research,[string keywords])]. For the sort type, we have 'pertinence',
    'article+' and 'article-' """

    
    # for pertinance, we check the number of keywords by research found
    if sort_type == 'pertinence':
        # we will build a list [(id_research,number_keyword)] and sort on number_keyword
        list_to_sort = []
        for i,k in research_list.items():
            list_to_sort.append((i,len(k)))
        def sort_key(elem):
            return elem[1]
        list_to_sort.sort(key=sort_key,reverse=True)


    # from + article to - article
    elif sort_type == 'article+' or sort_type == 'article-':
        # for each research, we count the number of article and build the list [(id,number_article)]
        list_to_sort = []
        for i,_ in research_list.items():
            research_object = Research.objects.get(id=i)
            number = len(Research_Article.objects.filter(research=research_object))
            list_to_sort.append((i,number))

        def sort_key(elem):
            return elem[1]
        
        if sort_type== 'article+':
            list_to_sort.sort(key=sort_key,reverse=True)
        else:
            list_to_sort.sort(key=sort_key)

        pass
    
    return_list = []
    # we build return list
    for id, _ in list_to_sort:
        keywords = []
        key_list = research_list[id]
        for k in key_list:
            keywords.append(k.word)
        keywords.sort()
        return_list.append((id,keywords))

    return return_list

def mock_research(research):
    """ For test. We arbitrarily associate a research with articles and clustering data for them.
    The position for a group clustering will be set around a point."""
    articles = Article.objects.all()
    size = len(articles)
    
    # we randomly associate article to the research
    import random
    number_article_by_research = random.randint(0,int(size/2))
    random_list = random.sample(range(0, size), number_article_by_research)
    number_topics = random.randint(0,int(size/50))
    topics = []
    for n in range(number_topics):
        center = (random.randint(0,600),random.randint(0,1000))
        topics.append(("topics " + str(n) , center))

    i = 0
    for article in articles:
        if i in random_list:
            Research_Article.objects.create(research=research,article=article)
            # the cluster data for the article. Choose randomly the topic and the position
            
            topic = topics[random.randint(0,number_topics - 1)]
            pos_x = topic[1][0] + random.randint(0,200)
            pos_y = topic[1][1] + random.randint(0,200)
            topic_name = topic[0]
            Cluster.objects.create(research=research,article=article,topic=topic_name,pos_x=pos_x,pos_y=pos_y)

        i +=1
    

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

def neighbour_article(article,research,number_neighbor=5):
    """ The function take an article, a research and process with cluster object, the nearest neighbor. By default, we take the 5 nearest.
    by iteration, we search around the article +-100 and if we doesnt have enough, the same but with +-200 around. We make max +-1000.
    The function return a list of article"""

    neighbour_articles = []
    distant = 100
    cluster_center_article = Cluster.objects.filter(article=article,research=research)
    #if the article doesn't exist in the cluster
    if not cluster_center_article.exists():
        return neighbour_articles

    cluster_center_article = cluster_center_article[0]
    center = (cluster_center_article.pos_x,cluster_center_article.pos_y)
    def distant_from_center(pos_x,pos_y):
        return (center[0] - pos_x)**2 + (center[1] - pos_y)**2

    nearest_cluster = []
    while True:
        if len(nearest_cluster)>=number_neighbor or distant > 1000:
            break
        
        cluster_list = Cluster.objects.filter(research=research, 
                                                pos_x__gte=center[0] - distant, 
                                                pos_x__lte=center[0] + distant,
                                                pos_y__gte=center[1] - distant,
                                                pos_y__lte=center[1] + distant)
        
        for cluster in cluster_list:
            # if there are some place, we add the cluster
            if len(nearest_cluster)<number_neighbor:
                nearest_cluster.append(cluster)
            else:
                # else, we check distant from center with all cluster in list
                # if there is one who is better, the new replace the ancient
                for i in range(len(nearest_cluster)):
                    ancient_distant = distant_from_center(nearest_cluster[i].pos_x,nearest_cluster[i].pos_y)
                    new_distant = distant_from_center(cluster.pos_x,cluster.pos_y)
                    if new_distant < ancient_distant:
                        nearest_cluster[i] = cluster
                        break

        distant += 100

    # we recuperate all article from cluster list
    for cluster in nearest_cluster:
        neighbour_articles.append(cluster.article)

    return neighbour_articles     



def get_Articles_Filtered(research,filters):
    """ The function take the research id and filters, build a list of article who match 
    the filters and return the list of the article id. If we choose id instead of the object, this is for save it in user session as a list of integer.
    The filters format is a dict() where each element isa block of filters. 
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
                #we retrieve all article_author objects for all author in the research name
                for author in author_list:
                    a = Article_Author.objects.filter(author=author)
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
                article_center = Article.objects.filter(doi=doi)
                if not article_center.exists():
                    empty = True
                    break
                # we get nearest neighbour. By default, the fonction neighbour_article get 5 article
                article_center = article_center[0]
                neighbour_articles_list = neighbour_article(article=article_center,research=research)
                # if first, the inial list is composed from the nearest neighbour of the first article
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
                    article_list = Article.objects.filter(Q(abstract__icontains=keyword) | Q(full_text__icontains=keyword))
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
    

def update_new_TableChoice(user,research,article_id_list):
    """When user make a new research filtering, the ancients are deleted and the new are written"""
    #we remove all row with this user
    TableChoice.objects.filter(user=user).delete()
    # we add new rows
    for id in article_id_list :
        TableChoice.objects.create(user=user,research=research,article=Article.objects.get(id=id))
    
def update_neighbour_TableChoice(user,research):
    """With an initial list of article, we add the nearest neighbour of these article in table choice"""
    tablechoice = TableChoice.objects.filter(user=user)
    for row in tablechoice:
        #we check if the article is to be displayed or not
        if not row.to_display:
            continue

        neighbours = neighbour_article(row.article,research)
        # we add these article. We check if the article is already in a row
        for article in neighbours:
            if TableChoice.objects.filter(user=user,research=research, article=article).exists():
                continue
            else:
                TableChoice.objects.create(user=user,research=research,article=article)

def update_article_to_display_TableChoice(user,research,list_id):
    """The function take a list of id object of TableChoice row and user. All row who is not in list_id,
    the boolean 'to_display' will be put to False. The function take user id by security. We check if all id
    in 'list_id' is owned by user because, the list of id come from the front-end by the user """

    # we check the ownership of the user for row in TableChoice
    for id in list_id:
        test = TableChoice.objects.get(id=id)
        if not test.user == user:
            return False

    #we update the boolean 'to_display'
    tablechoice = TableChoice.objects.filter(user=user,research=research)
    for row in tablechoice:
        if not row.id in list_id:
            row.to_display = False


def all_display_TableChoice(user,research):
    """ Reset all article so we can display all article"""    
    tablechoice = TableChoice.objects.filter(user=user,research=research)
    for row in tablechoice:
        row.to_display = True

    