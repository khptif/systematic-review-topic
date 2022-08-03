from threading import Thread
from django.http import HttpResponse
from django.shortcuts import render
from matplotlib import use
from BackEnd.models import Number_trial 
from BackEnd.views import research_create
from DataBase.functions.view_functions import *
import DataBase.functions.PDF_download as pdf
from BackEnd.functions.scatter_with_hover import scatter_with_hover
import json

def get_max(request):
    # we check if we have all parameters
    if not "search_term" in request.GET:
        return HttpResponse("No search",status=400)

    if not "date_begin" in request.GET or not "date_end" in request.GET:
        return HttpResponse("No dates",status=400)
    
    search_term = request.GET["search_term"]
    date_begin = request.GET["date_begin"]
    date_begin =  datetime.datetime.strptime(date_begin,"%Y/%m/%d").date()
    date_end = request.GET["date_end"]
    date_end = datetime.datetime.strptime(date_end,"%Y/%m/%d").date()

    number_article = max_article(search_term,date_begin,date_end)

    return HttpResponse(str(number_article),status=200)

def fetch_article(request):
    # we check if we have the research id
    if not "research_id" in request.GET:
        return HttpResponse("No research id",status=400)
    
    id = int(request.GET["research_id"])
    # we check if the research exists
    research = Research.objects.filter(id=id)
    if not research.exists():
        return HttpResponse("Research doesn't exist",status=400)
    from programmeDjango.settings import NUMBER_TRIALS
    make_research(research.search,research,research.year_begin,research.year_end,NUMBER_TRIALS)
    
    return HttpResponse("",status=200)

def download_article(request):
    # we check if we have the id of the article
    if not "article_id" in request.GET:
        return HttpResponse("No article",status=400)

    # we check if the article exists in our database
    article_id = request.GET["article_id"]
    article = Article.objects.filter(id=int(article_id))

    if not article.exists():
        return HttpResponse("Article doesn't exist",status=400)
    
    article = article[0]

    # we create a thread to download the article and return the http message
    def download(article):
        if pdf.download_from_URL(article,True):
            article.is_file_get = True
            article.save()

    t = Thread(target=download,args=(article,))
    t.setDaemon(True)
    t.start()  

    return HttpResponse("",status=200)

def create_plot(request):
    # we check if we have the research id
    if not "research_id" in request.GET:
        return HttpResponse("No research id",status=400)
    
    id = int(request.GET["research_id"])
    # we check if the research exists
    research = Research.objects.filter(id=id)
    if not research.exists():
        return HttpResponse("Research doesn't exist",status=400)
    
    # we create the plot
    from programmeDjango.settings import PLOT_DATA
    scatter_with_hover(research[0],PLOT_DATA + f"/research_{id}_plot.html")

    return HttpResponse("",status=200)

def get_plot(request):
    # we check if we have the research id
    if not "research_id" in request.GET:
        return HttpResponse("No research id",status=400)
    
    id = int(request.GET["research_id"])
    # we check if the research exists
    research = Research.objects.filter(id=id)
    if not research.exists():
        return HttpResponse("Research doesn't exist",status=400)
    
    # we check if the plot exists
    import os
    from programmeDjango.settings import PLOT_DATA
    path_to_plot = PLOT_DATA + f"/research_{id}_plot.html"
    if not os.path.exists(path_to_plot):
        return HttpResponse("Plot doesn't exist",status=400)
    
    
    return render(request,path_to_plot)

def get_plot_html_string(request):
    # we check if we have the research id
    if not "research_id" in request.GET:
        return HttpResponse("No research id",status=400)
    
    id = int(request.GET["research_id"])
    # we check if the research exists
    research = Research.objects.filter(id=id)
    if not research.exists():
        return HttpResponse("Research doesn't exist",status=400)
    
    # we check if the plot exists
    import os
    from programmeDjango.settings import PLOT_DATA
    path_to_plot = PLOT_DATA + f"/research_{id}_plot.html"
    if not os.path.exists(path_to_plot):
        return HttpResponse("Plot doesn't exist",status=400)
    
    # we extract string from html plot and return it
    data=''
    with open(PLOT_DATA + "/research_{id}_plot.html".format(id=id), 'r') as file:
            data = file.read()
    
    #we send the data by json
    content = json.dumps(data)
    return HttpResponse(content,status=200)

def get_final(request):
    # we check if we have the research id
    if not "research_id" in request.GET or not "user_id" in request.GET:
        return HttpResponse("No research id or user id",status=400)
    
    id_user = int(request.GET["user_id"])
    id_research = int(request.GET["research_id"])
    # we check if the research exists and user exist
    research = Research.objects.filter(id=id_research)
    user = CustomUser.objects.filter(id=id_user)
    if not research.exists() or not user.exists():
        return HttpResponse("Research doesn't exist or user id",status=400)

    # we check if there is a tablechoice for this research and user
    table = TableChoice.objects.filter(research=research[0],user=user[0])
    if not table.exists():
        return HttpResponse("There is no table",status=400)
    
    path_to_zip = create_final_file(research[0],user[0])

    path = open(path_to_zip, 'rb')
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type="application/zip")
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename={name_file}".format(name_file="final_articles.zip")
    # Return the response value
    return response

# Create your views here.


