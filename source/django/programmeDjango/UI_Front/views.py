from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout
import random
import requests
import json
from BackEnd.functions.view_functions import max_article

from UI_Front.models import *
from DataBase.models import *
from BackEnd.models import *

from UI_Front.functions.select_functions import * 
from UI_Front.functions.accueil_functions import *
from UI_Front.functions.tablechoice_functions import *
from UI_Front.functions.login_functions import *
from UI_Front.functions.user_page_functions import *
from UI_Front.functions.utils_functions import *

from programmeDjango.settings import BACKEND_HOST,BACKEND_PORT
from programmeDjango.settings import NUMBER_TRIALS

@login_required(login_url='/login')
def page_accueil(request):

    variables = dict()
    research_form = Research_form()
    historical_form = Historical_form()

    variables['research_form'] = research_form
    variables['historical_form'] = historical_form
    variables['host'] = request.get_host()
    variables['research_created'] = ""

    # if we receive POST form
    if request.method == 'POST':
        submit = request.POST['submit']
        # if we evaluate the number of article
        if submit == 'evaluate':
            research_form = Research_form(request.POST)
            variables['research_form'] = research_form
            if research_form.is_valid():
                search = research_form.cleaned_data['search']
                r = requests.get("http://" + BACKEND_HOST + ":" + BACKEND_PORT + "/max_article?search=" + search)
                if r.status_code < 400:
                    data = json.loads(r.text)
                    variables['number_article'] = data["max_article"]
                else:
                    variables['number_article'] = "error http status " + str(r.status_code)

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

            total_article = max_article(search)
            research = Research.objects.create(user=user,search=search,year_begin=year_begin,year_end=year_end,max_article=total_article)

            # set the keywords of the research
            # keywords
            for w in request.session['keywords']:
                Keyword.objects.create(research=research,word=w)

            #we send the request
            r = requests.get("http://" + BACKEND_HOST + ":" + BACKEND_PORT + "/research?research_id=" + str(research.id))
            if r.status_code < 400:
                variables['research_created'] = "You research has been created and is running"
            else:
                research.delete()
                variables['research_created'] = "error http status " + str(r.status_code) + " " + str(r.text)


        #if user search historical research
        if submit == 'historical':
            historical_form = Historical_form(request.POST)
            variables['historical_form'] = historical_form
            if historical_form.is_valid():
                search = historical_form.cleaned_data['search']
                keywords = word_list(search)
                
                # we check the Keywords object who match
                # we build a dict() : dict[research id] = list of keywords who match the search
                research_list = dict()
                for k in keywords:
                    # we take only research there are finish
                    keyword_list = Keyword.objects.all().filter(word=k,research__is_finish=True)
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
def page_user(request):
    variables = dict()
    variables['user'] = request.user

    if request.method == "POST":
        if "submit" in request.POST:
            research_id = request.POST['research_id']
            # if this is a request for check process
            if request.POST['submit'] == "check":
                r = requests.get("http://" + BACKEND_HOST + ":" + BACKEND_PORT + "/check?research_id=" + str(research_id))
                if r.status_code < 400:
                    data_json = json.loads(r.text)
                    variables["id_check"] = research_id
                    if data_json["is_running"]:
                        variables["is_running"] = "running"
                    else:
                        variables["is_running"] = "not running"

            if request.POST['submit'] == "delete":
                requests.get("http://" + BACKEND_HOST + ":" + BACKEND_PORT + "/delete?research_id=" + str(research_id))

    #we get user's research that are finished
    variables['research_finished'] = Research.objects.filter(user = request.user, is_finish = True)
    # we get user's research that are still running and in article's research step
    variables['research_step_article'] = []
    for r in  Research.objects.filter(user = request.user, is_running = True, step="article",is_finish = False):
        variables['research_step_article'].append(r)
    
    # we get user's research that are still running and in preprocessing step. 
    variables['research_step_processing'] = []
    for r in  Research.objects.filter(user = request.user, is_running = True, step="processing",is_finish = False):
        variables['research_step_processing'].append(r)

    # we get user's research that are still running and in clustering step.
    variables['research_step_clustering'] = []
    for r in  Research.objects.filter(user = request.user, is_running = True, step="clustering",is_finish = False):
        variables['research_step_clustering'].append(r)
    
    #we give the number of trials max
    variables['number_trials'] = NUMBER_TRIALS


    a = TableChoice.objects.filter(user=request.user)
    
    if a.exists():
        research_id = a[0].research.id
        variables['research_id'] = research_id
    return render(request,'page_user.html',variables)



@login_required(login_url='/login')
def page_select(request):
    variables = dict()
    # when we receive all data for filters
    if request.method == 'POST':
        submit = request.POST['submit'] 
        if submit == 'generate':
            research_id = int(request.POST.get("research_id"))
            research = Research.objects.get(id=research_id)
            # we transform the POST data
            blocks_filters = filters_manager(request.POST)
            # we get a list of id article who match all the filters
            id_article_list = get_Articles_Filtered(research=research,filters=blocks_filters)
            # we save this list in session user
            request.session['id_article_list'] = id_article_list
            request.session['id_research'] = research_id
            variables['number_article'] = len(id_article_list)
            variables['AreYouSure'] = True
            return render(request,'page_select.html',variables)
        
        elif submit == 'continue':
            user = request.user
            research_id = request.session['id_research']
            research = Research.objects.get(id=research_id)

            update_new_TableChoice(user=user,research=research,article_id_list =request.session['id_article_list'])
            update_neighbour_TableChoice(user=user,research=research)
            
            request.session['id_article_list'] = []
            request.session['id_research'] = 0
            return redirect("/table_choice?research_id="+str(research_id))

        elif submit == 'cancel':
            request.session['id_article_list'] = []
            pass

        

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
    variables['cluster_list'] = Cluster.objects.filter(research=research)
    
    #list of article
    variables['article_list'] = Article.objects.filter(research_article__research=research)

    #id of the research
    variables['research_id'] = id
    

    return render(request, 'page_select.html', variables)


@login_required(login_url='/login')
def page_table_choice(request):
    variables = dict()
    #we check if the GET parameter is there and if the id match with one of the existant research
    if not 'research_id' in request.GET:
        return redirect("/accueil")
    id= request.GET.get('research_id')
    if not id.isnumeric():
        return redirect("/accueil")
    elif not Research.objects.filter(id=request.GET.get('research_id')).exists():
        return redirect('/accueil')

    
    if request.method =='POST':
        check_list = []
        if 'check_row' in request.POST:
            check_list = request.POST.getlist('check_row')
        submit = request.POST.get('submit')
        
        user = request.user
        research = Research.objects.get(id=int(request.GET.get('research_id')))
        if submit == 'iterate':        
            update_article_to_display_TableChoice(user=request.user,research=research,list_id=check_list)
            update_neighbour_TableChoice(user=user,research=research)
        elif submit == 'reset':
            reset_TableChoice(user=user,research=research)
        elif submit == 'finish':
            update_article_to_display_TableChoice(user=request.user,research=research,list_id=check_list)
            return test_download_finalzip(request=request,user=user,research=research)

    user = request.user
    research = Research.objects.get(id=request.GET.get('research_id'))
    tablechoice_list = TableChoice.objects.filter(user=user,research=research,to_display=True)
    
    variables['row_list'] = tablechoice_list
    
        
    return render(request,"page_table_choice.html",variables)

# Create your views here.
