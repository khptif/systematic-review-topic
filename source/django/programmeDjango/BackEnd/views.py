from django.http import HttpResponse

from BackEnd.functions.view_functions import *

def restart_research(request):
    # we check if we have the Get parameter.
    if not "research_id" in request.GET:
        return HttpResponse("No id parameter",status=400)

    # we check if the research exists 
    id = request.GET["research_id"]
    research = Research.objects.filter(id=int(id))
    if not research.exists():
        return HttpResponse("Research doesn't exists",status=400)
    research = research[0]

    relaunch_if_fault(research.id)
    return HttpResponse("",status=200)

def research_create(request):
    # we check if we have the Get parameter.
    if not "research_id" in request.GET:
        return HttpResponse("No id parameter",status=400)

    # we check if the research exists 
    id = request.GET["research_id"]
    research = Research.objects.filter(id=int(id))
    if not research.exists():
        return HttpResponse("Research doesn't exists",status=400)
    research = research[0]
    # we check if the research is already running or finished
    if research.is_running or research.is_finish:
        return HttpResponse("Research already running or finished",status=400)
    
    launch_process(research)

    return HttpResponse("",status=200)

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

def check_research(request):
    # we check if we have the Get parameter.
    if not "research_id" in request.GET:
        return HttpResponse("No id parameter",status=400)

    # we check if the research exists 
    id = request.GET["research_id"]
    research = Research.objects.filter(id=int(id))
    if not research.exists():
        return HttpResponse("Research doesn't exists",status=400)
    
    research = research[0]
    # we check if the research is still running in a thread
    return HttpResponse(str(check(research)),status=200)