from threading import Thread
from django.http import HttpResponse
from django.shortcuts import render
from matplotlib import use 
from BackEnd.views import research_create
from DataBase.functions.view_functions import *
import BackEnd.functions.PDF_download as pdf
from BackEnd.functions.scatter_with_hover import scatter_with_hover

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
    # we check if the article is already in our machine
    if article.is_file_get:
        return HttpResponse("Article already downloaded",status=400)

    # we create a thread to download the article and return the http message
    def download(article):
        from programmeDjango.settings import TEMPORARY_DATA

        if pdf.download_from_URL(article):
            article.is_file_get = True
            article.save()

    t = Thread(target=download,args=(article))
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
    
    return HttpResponse(data,status=200)

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


