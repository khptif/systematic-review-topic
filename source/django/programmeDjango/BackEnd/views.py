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