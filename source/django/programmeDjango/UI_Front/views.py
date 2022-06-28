
from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout


from urllib3 import HTTPResponse

from UI_Front.models import *
from DataBase.models import *
from BackEnd.models import *

from UI_Front.functions.select_functions import * 
from UI_Front.functions.accueil_functions import *
from UI_Front.functions.tablechoice_functions import *
from UI_Front.functions.login_functions import *
from UI_Front.functions.user_page_functions import *
from UI_Front.functions.utils_functions import *


from programmeDjango.settings import NUMBER_TRIALS, PLOT_DATA


from BackEnd.functions.view_functions import *
from remote_functions import *

#### Page Accueil #####
@login_required(login_url='/login')
def page_accueil(request):

    variables = dict()
    research_form = Research_form(initial={"From":datetime.datetime(1800,1,1).date(),"To":datetime.datetime.now().date()})
    historical_form = Historical_form()

    variables['research_form'] = research_form
    variables['historical_form'] = historical_form
    variables['host'] = request.get_host()
    variables['research_created'] = ""

    ## POST REQUEST ##
    # if we receive POST form
    if request.method == 'POST':
        submit = request.POST['submit']
        # if we evaluate the number of article
        if submit == 'evaluate':
            research_form = Research_form(request.POST)
            variables['research_form'] = research_form
            if research_form.is_valid():
                search = research_form.cleaned_data['search']
                begin = research_form.cleaned_data['From']
                end = research_form.cleaned_data['To']
                from programmeDjango.settings import is_decentralized
                if is_decentralized:
                    variables['number_article'] = get_max_article_remote(search,begin,end)
                else:
                    variables['number_article'] = max_article(search,begin,end)
                

        # if we give a new research
        elif submit == 'research':
            research_form = Research_form(request.POST)
            variables['research_form'] = research_form
            if research_form.is_valid():
                search = research_form.cleaned_data['search']
                year_begin = research_form.cleaned_data['From']
                year_end = research_form.cleaned_data['To']

                keywords = word_list(search)
                request.session["keywords"] = keywords
                keys_values = [('search',search),('year_begin',year_begin.strftime("%Y/%m/%d")),('year_end',year_end.strftime("%Y/%m/%d"))]
                # we keep the variables in the session
                # we give theses variables to the template and display a "are you sure" window before accept the research
                for k in keys_values:
                    request.session[ k[0] ] = k[1]
                    variables[ k[0] ] = k[1]

                variables['are_you_sure'] = True
                
                
        #if user cancel the research
        elif submit == 'cancel':
            search = request.session['search']
            year_begin = datetime.datetime.strptime(request.session['year_begin'],"%Y/%m/%d").date()
            year_end = datetime.datetime.strptime(request.session['year_end'],"%Y/%m/%d").date()
            research_form = Research_form(initial = {'search': search ,'From':year_begin,'To':year_end})

            variables['research_form'] = research_form

        #if user commit the research
        elif submit == 'continue':
            user = request.user
            year_begin = datetime.datetime.strptime(request.session['year_begin'],"%Y/%m/%d").date()
            year_end = datetime.datetime.strptime(request.session['year_end'],"%Y/%m/%d").date()
            search = request.session['search']
            from programmeDjango.settings import is_decentralized

            if is_decentralized:
                total_article = get_max_article_remote(search,year_begin,year_end)
            else:
                total_article = max_article(search,year_begin,year_end)

            research = Research.objects.create(user=user,search=search,year_begin=year_begin,year_end=year_end,max_article=total_article)

            # set the keywords of the research
            # keywords
            for w in request.session['keywords']:
                Keyword.objects.create(research=research,word=w)

            #we send the request
            from programmeDjango.settings import is_decentralized
            if is_decentralized:
                if begin_research_remote(research):
                    variables['research_created'] = "You research has been created and is running"
                else:
                    variables['research_created'] = "error in launchin research"
            else:
                if launch_process(research):
                    variables['research_created'] = "You research has been created and is running"
                else:
                    variables['research_created'] = "error in launchin research"
            
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
                    key_regex = r".*" + k + r".*"
                    keyword_list = Keyword.objects.all().filter(word__iregex=key_regex,research__is_finish=True)
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
            if request.POST["submit"] == "delete_all":
                # we delete all research 
                Research.objects.all().delete() 
            
            elif request.POST["submit"] == "restart_fault":
                #we restart all research with fault
                from programmeDjango.settings import is_decentralized
                if is_decentralized:
                    from remote_functions import relaunch_if_fault_remote
                    relaunch_if_fault_remote()
                else:
                    relaunch_if_fault()

            else:    
                research_id = request.POST['research_id']
                research = Research.objects.get(id=research_id)
                # if this is a request for check process
                if request.POST['submit'] == "check":
                    from programmeDjango.settings import is_decentralized
                    if is_decentralized:
                        from remote_functions import check_research_remote
                        variables["is_running"] = check_research_remote(research)
                    else:
                        variables["is_running"] = check(research)
            
                if request.POST['submit'] == "delete":
                    delete(research)

            
                
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
            blocks_filters = filters_manager(research,request.POST)
            # we get a list of id article who match all the filters
            id_article_list = get_Articles_Filtered(research=research,filters=blocks_filters)
            # we save this list in session user
            request.session['id_article_list'] = id_article_list
            request.session['id_research'] = research_id
            variables['number_article'] = len(id_article_list)
            variables['AreYouSure'] = True
            #we save data filters if the user cancel and return to select page
            request.session["filter_data"] = filter_recover_data(request.POST)

            return render(request,'page_select.html',variables)
        
        elif submit == 'continue':
            user = request.user
            research_id = request.session['id_research']
            research = Research.objects.get(id=research_id)

            #we update the new table choice with the article selected without their neighbour
            update_new_TableChoice(user=user,research=research,article_id_list =request.session['id_article_list'])
            
            request.session['id_article_list'] = []
            request.session['id_research'] = 0
            return redirect("/table_choice?research_id="+str(research_id))

        elif submit == 'cancel':
            if "filter_data" in request.session:
                variables["filter_data"] = request.session["filter_data"]
                variables["cancel"]=True

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

    #we give the plot html
    from programmeDjango.settings import is_decentralized
    data=""
    research_id = research.id
    if is_decentralized:
        from programmeDjango.settings import DataBase_host_adresse as adresse
        from programmeDjango.settings import DataBase_host_port as port
        from programmeDjango.settings import DataBase_SSL as is_ssl

        if is_ssl:
            variables["path_plot"] = f"https://{adresse}:{port}/get_plot?research_id={research_id}"
        else:
            variables["path_plot"] = f"http://{adresse}:{port}/get_plot?research_id={research_id}"

        from remote_functions import get_plot_remote
        r = get_plot_remote_string(research)
        if not r == False:
            data = r
    else:
        with open(PLOT_DATA + "/research_{id}_plot.html".format(id=id), 'r') as file:
            data = file.read()
        variables["path_plot"] = f"/plot?research_id={research_id}"
    
    variables["plot_html"] = data

    #we give a list of all topics
    variables["list_topics"] = list(set(Cluster.objects.filter(research=research).values_list("topic",flat=True)))
        
    return render(request, 'page_select.html', variables)


@login_required(login_url='/login')
def page_table_choice(request):
    variables = dict()
    current_page = 1
    from programmeDjango.settings import NUMBER_ARTICLE_BY_PAGE
    #we check if the GET parameter is there and if the id match with one of the existant research
    if not 'research_id' in request.GET:
        return redirect("/accueil")
    id= request.GET.get('research_id')
    if not id.isnumeric():
        return redirect("/accueil")
    elif not Research.objects.filter(id=request.GET.get('research_id')).exists():
        return redirect('/accueil')
    elif "page" in request.GET:
        current_page = int(request.GET["page"])
        # we check if the page is good.
        # if too low, we redirect to first page
        if current_page < 1:
            current_page = 1
        # if too high, we redirect to last page
        research = Research.objects.get(id=int(request.GET.get('research_id')))
        number_Article = TableChoice.objects.filter(research=research).count()
        if int(request.GET["page"]) > int(number_Article/NUMBER_ARTICLE_BY_PAGE) + 1:
            current_page = int(number_Article/NUMBER_ARTICLE_BY_PAGE) + 1

    #if we receive a POST request
    if request.method =='POST':
        check_list = []
        if 'check_row' in request.POST:
            check_list = request.POST.getlist('check_row')
        submit = request.POST.get('submit')
        
        user = request.user
        research = Research.objects.get(id=int(request.GET.get('research_id')))
        number_Article = TableChoice.objects.filter(research=research).count()
        if submit == 'iterate':
            update_article_is_check_TableChoice(user=request.user,research=research,list_id=check_list)
            update_article_to_display_TableChoice(user=request.user,research=research,list_id=check_list)
            update_neighbour_TableChoice(user=user,research=research)
            return redirect("/table_choice?research_id={id}".format(id=str(research.id)))
        elif submit == 'reset':
            reset_TableChoice(user=user,research=research)
            return redirect("/table_choice?research_id={id}".format(id=str(research.id)))
        elif submit == 'finish':
            update_article_is_check_TableChoice(user=request.user,research=research,list_id=check_list)
            update_article_to_display_TableChoice(user=request.user,research=research,list_id=check_list)
            return redirect(download_finalzip(research=research,user=user))
        elif submit == 'previous':
            if current_page == 1:
                pass
            else:
                update_article_is_check_TableChoice(user=request.user,research=research,list_id=check_list)
                return redirect("/table_choice?research_id={id}&page={page}".format(id=str(research.id),page=str(current_page - 1)))
        elif submit == 'next':
            if current_page == int(number_Article/NUMBER_ARTICLE_BY_PAGE) + 1:
                pass
            else:
                update_article_is_check_TableChoice(user=request.user,research=research,list_id=check_list)
                return redirect("/table_choice?research_id={id}&page={page}".format(id=str(research.id),page=str(current_page + 1)))

    user = request.user
    research = Research.objects.get(id=request.GET.get('research_id'))
    tablechoice_list = TableChoice.objects.filter(user=user,research=research,to_display=True).order_by("id")

    #we define variable about number of articles
    variables['number_Article_initial'] = TableChoice.objects.filter(user=user,research=research,is_initial=True).count()
    variables['number_Article_neighbour'] = TableChoice.objects.filter(user=user,research=research,is_initial=False,to_display=True,is_check=False).count()
    variables['number_Article_chosen'] = TableChoice.objects.filter(user=user,research=research,is_check=True).count()

    #we define the interval of article for the current page
    first_article = (current_page - 1)*NUMBER_ARTICLE_BY_PAGE
    last_article = current_page * NUMBER_ARTICLE_BY_PAGE
    
    #we check if last_article is not greater than the size of the list
    if last_article < tablechoice_list.count():
        variables['row_list'] = tablechoice_list[first_article:last_article]
        variables["last_page"] = False
    else:
        variables['row_list'] = tablechoice_list[first_article:]
        variables["last_page"] = True
    if current_page == 1:
        variables["first_page"] = True
    else:
        variables["first_page"] = False
    
    variables["current_page"] = current_page
    if tablechoice_list.count()%NUMBER_ARTICLE_BY_PAGE == 0:
        variables["total_page"] = int(tablechoice_list.count()/NUMBER_ARTICLE_BY_PAGE)
    else:
        variables["total_page"] = int(tablechoice_list.count()/NUMBER_ARTICLE_BY_PAGE) + 1
        
    return render(request,"page_table_choice.html",variables)


@login_required(login_url='/login')
def render_plot(request):
    """it render the html file that represent the plot of a research."""
    #we check if there are GET parameter "research"
    if not "research" in request.GET:
        return redirect("/accueil")
    #we check if the plot file exist
    id = request.GET["research"]
    if not os.path.exists(PLOT_DATA + "/research_{id}_plot.html".format(id=str(id))):
        return redirect("/accueil")
    
    #we render the html plot
    return render(request,PLOT_DATA + "/research_{id}_plot.html".format(id=str(id)))

# Create your views here.
