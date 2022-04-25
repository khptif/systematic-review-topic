import re
from DataBase.models import *
from UI_Front.functions.utils_functions import *
from django import forms
from django.core.exceptions import ValidationError




def errorParsingResearch(string_to_parse):
    """ Check if there is error in the search string for the research"""
    lower_string = string_to_parse.lower()
    char=re.findall("(?![a-z]|\(|\)|[0-9]|\-|\"|,|;|\s).",lower_string)
    # check if there are forbidden characters. Only [a-z], [0-9], '-', double quotes, comma, ';' ,parenthesis and space allowed
    # if founded, return forbidden characters
    if char:
        forbidden_char = ""
        for c in char:
            forbidden_char += " ' " + c + " ' "
        
        return (False, "Forbidden characters : " + forbidden_char)

    # check if there are words
    words = re.findall("[a-z0-9\-]+",lower_string)
    if not words:
        return (False, " Error, there is no word")
    # check if the words are not only a single '-'
    keyword = False
    for w in words:
        if not w=='-':
            keyword = True
            break

    if not keyword:
        return (False, "Error, thers is no keyword")

    #check if for a opened quote there is a closed quote
    # we check if there is a even number of quotes
    quotes = re.findall("\"",lower_string)
    if not len(quotes)%2 == 0:
        return (False, "Error, it misses a quote")

    #check if between each keywords, there is a [ ',' ';' ',(' '),' ';(' ');']
    # it must not exist empty keywords between these characters
    number_keyword = 0
    quotes_keyword = re.findall("\"[a-z0-9\-\s]*\"",lower_string)
    number_keyword += len(quotes_keyword)
    s=lower_string
    for qw in quotes_keyword:
        s = s.replace(qw,"")
    single_keyword = re.findall("[a-z0-9\-]+",s)
    number_keyword += len(single_keyword)
    for sw in single_keyword:
        s = s.replace(sw,"")
    # we replace espace by empty character.
    s = s.replace(" ","")
    # now, it must exist (number_keyword -1) characters from [ ',' ';' ',(' '),' ';(' ');']
    # we extract the cases with parenthesis
    parenthesis = re.findall("[,;]{1}\(",s)
    s = s.replace(",(","")
    s = s.replace(";(","")
    
    p = re.findall("\)[,;]{1}",s)
    parenthesis.extend(p)
    # we delete parenthesis in string with their [',' ';'].
    for p in parenthesis:
        s = s.replace(p,"")
    #we recuperate the commas
    comma = re.findall("[,;]{1}",s)

    occurence = 0
    size = len(parenthesis) + len(comma)
    if not size == number_keyword - 1:
        if size < number_keyword - 1:
            return (False,"Error, it misses some comma")
        elif size > number_keyword -1:
            return (False, "Error, there are too comma") 
    
    #check if into quotes there are only [a-z0-9],'-' and space
    # we delete good quotes keywords and we check if there are still quote
    quotes_word = re.findall("\"[a-z0-9\-\s]*\"",lower_string)
    s = lower_string
    for qw in quotes_word:
        s = s.replace(qw,"")
    
    bad_quotes = re.findall("\"",s)
    if bad_quotes:
        return (False,"Error, one of the quotes keyword is bad")

    #check if between each keywords there is a 

        
    #check parenthesis. opened parenthesis must have a closed one and be before closed one.
    # During the parsing, for var n, '(' => +1, ')' => -1. If negative value, problem with ')'.
    # If negatif value, too many ')'. If not zero after parsing, too many '('
    n = 0
    for c in lower_string:
        if c == '(':
            n += 1
        elif c == ')':
            n -= 1

        if n < 0 :
            return (False, "Error with ' ) ', closed parenthesis")
        
    if not n == 0:
        return (False,"Error with ' ( ', opened parenthesis")

    # return True if pass all checks

    return (True,"")

def errorParsingHistorical(search_string):
    """ Check if there are errors in the string search for historical"""
    lower_string = search_string.lower()

    char=re.findall("(?![a-z0-9\-\"]| ).",lower_string)
    # check if there are forbidden characters. Only [a-z] and space allowed
    # if founded, return forbidden characters
    if char:
        forbidden_char = ''
        for c in char:
            forbidden_char += c
            forbidden_char += ' '
        return (False, "Forbidden characters : " + forbidden_char)

    # check if there are words
    quotes_words = re.findall("\"[a-z0-9\-\s]+\"",lower_string)
    s = lower_string
    for qw in quotes_words:
        s=s.replace(qw,"")
    single_words = re.findall("[a-z0-9\-]+",s)
    words = []
    words.extend(quotes_words)
    words.extend(single_words)

    if not words:
        return (False, " Error, there is no word")
    
    return (True,'')

class Research_form(forms.Form):
    search = forms.CharField(max_length=512)
    year_begin = forms.IntegerField(min_value=1990)
    year_end = forms.IntegerField(min_value=1990)

    def clean(self):
        data = super(Research_form,self).clean()
        year_begin = data['year_begin']
        year_end = data['year_end']
        if year_end < year_begin :
            raise ValidationError(" year_end must be higher or equal than year_begin")
        else:
            return data

    def clean_search(self):
        data = super(Research_form,self).clean()
        search = data['search']
        check , error = errorParsingResearch(search)
        if check:
            return search
        else:
            raise ValidationError(error)


class Historical_form(forms.Form):
    search = forms.CharField(max_length=1024)

    def clean_search(self):
        data = super(Historical_form,self).clean()
        search = data['search']
        check , error = errorParsingHistorical(search)
        if check:
            return search
        else:
            raise ValidationError(error)

def word_list(string_to_parse):
    """ From a search string that was control if there is bad characters,
     extract all keywords and return them"""
   
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
    
