from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout
import random
import re

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
    in this format: [(id research,[string keywords])]"""

    
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


@login_required(login_url='/login')
def page_accueil(request):

    variables = dict()
    research_form = Research_form()
    historical_form = Historical_form()

    variables['research_form'] = research_form
    variables['historical_form'] = historical_form
    variables['host'] = request.get_host()

    # if we receive POST form
    if request.method == 'POST':
        submit = request.POST['submit']
        # if we evaluate the number of article
        if submit == 'evaluate':
            research_form = Research_form(request.POST)
            variables['research_form'] = research_form
            if research_form.is_valid():
                variables['number_article'] = random.randint(0,100000)
                
        # if we give a new research
        elif submit == 'research':
            research_form = Research_form(request.POST)
            variables['research_form'] = research_form
            if research_form.is_valid():
                search = research_form.cleaned_data['search']
                year_begin = research_form.cleaned_data['year_begin']
                year_end = research_form.cleaned_data['year_end']

                keywords = word_list(search)
                keys_values = [('search',search),('year_begin',year_begin),('year_end',year_end),('keywords',keywords)]
                # we keep the variables in the session
                # we give theses variables to the template and display a "are you sure" window before accept the research
                for k in keys_values:
                    request.session[ k[0] ] = k[1]
                    variables[ k[0] ] = k[1]

                variables['are_you_sure'] = True
                
                
        #if user cancel the research
        elif submit == 'cancel':
            search = request.session['search']
            year_begin = request.session['year_begin']
            year_end = request.session['year_end']
            research_form = Research_form(initial = {'search': search ,'year_begin':year_begin,'year_end':year_end})

            variables['research_form'] = research_form

        #if user commit the research
        elif submit == 'continue':
            user = request.user
            year_begin = datetime.date(request.session['year_begin'],1,1)
            year_end = datetime.date(request.session['year_end'],1,1)
            search = request.session['search']

            research = Research.objects.create(user=user,search=search,year_begin=year_begin,year_end=year_end)

            # set the keywords of the research
            # keywords
            for w in request.session['keywords']:
                Keyword.objects.create(research=research,word=w)

        #if user search historical research
        if submit == 'historical':
            historical_form = Historical_form(request.POST)
            variables['historical_form'] = historical_form
            if historical_form.is_valid():
                search = historical_form.cleaned_data['search']
                keywords = word_list(search)
                print(keywords)
                # we check the Keywords object who match
                # we build a dict() : dict[research id] = list of keywords who match the search
                research_list = dict()
                for k in keywords:
                    keyword_list = Keyword.objects.all().filter(word=k)
                    for key in keyword_list:
                        if not key.research.id in research_list:
                            research_list[key.research.id] = []
                        research_list[key.research.id].append(key)
                # we sort the result according to sort_type given by user
                sort_type = request.POST.get('sort_type')
                variables['research_list'] = sort_historical(research_list,sort_type)
            

    return render(request,'page_accueil.html',variables)


def page_login(request):

    login_form = LoginForm()
    sign_form = SignForm()

    if request.method == 'POST':
        submit = request.POST.get('submit')
        if submit == 'login':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                email = login_form.cleaned_data['email']
                password = login_form.cleaned_data['password']
                
                user = authenticate(email=email, password=password)
                if user is not None:
                    login(request, user)
                    redirection = '/accueil'
                    if next in request.GET:
                        redirection = request.GET.get('next')
                    return redirect(redirection)

        elif submit == 'sign':
            sign_form = SignForm(request.POST)
            if sign_form.is_valid():
                email = sign_form.cleaned_data['email']
                password = sign_form.cleaned_data['password2']
                user = CustomUser.objects.create_user(email=email,password=password)
                login(request,user)
                redirection = '/accueil'
                if next in request.GET:
                    redirection = request.GET.get('next')
                return redirect(redirection)

    variables = dict()
    variables['login_form'] = login_form
    variables['sign_form'] = sign_form
    return render(request,'page_login.html',variables)

def page_logout(request):
    logout(request)
    return redirect('/login')

@login_required(login_url='/login')
def page_utilisateur(request):
    variables = dict()
    variables['user'] = request.user
    return render(request,'page_utilisateur.html',variables)

@login_required(login_url='/login')
def page_select(request):
    variables = dict()
    # we check if we have the id of the research and this id is available
    if not 'research_id' in request.GET:
        return redirect('/accueil')
    id = request.GET.get('research_id')
    research_exist = Research.objects.filter(id=id).exists()
    if not research_exist:
        return redirect('/accueil')

    # we give all the variable
    # list of cluster
    research = Research.objects.get(id=id)
    cluster_list = Cluster.objects.filter(research=research)
    topic_list = []
    research_article = Research_Article.objects.filter(research=research)
        
    return render(request, 'page_select.html', variables)

# Create your views here.
