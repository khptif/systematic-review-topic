from django.http import HttpResponse

from BackEnd.functions.view_functions import *

import BackEnd.functions.text_processing as text_processing

from DataBase.models import *
from BackEnd.models import *
from UI_Front.models import *

import os

import json
from sklearn.feature_extraction.text import TfidfVectorizer
import signal
from glob import glob


from programmeDjango.settings import NUMBER_THREADS_ALLOWED
from programmeDjango.settings import NUMBER_TRIALS

# remove stopwords and one and two characters words
list_stopwords = text_processing.create_stopwords()

# Create your views here.
        
def get_max_article(request):
    """Receive a http request with the search string in a json and return a json with the max article of the research"""

    if not "search" in request.GET:
        return HttpResponse(content="",status=400)
    
    search = request.GET["search"]
    print(search)
    if search == "":
        return HttpResponse(json.dumps({"max_article":-1}))
    else:
        
        total = max_article(search)
        return HttpResponse(json.dumps({"max_article" : total})) 
            
def launch_backend_process(request):
    """ Receive a http request with the id of the research to make.
        We check if all is good before launch the process.
        We fork a new process where the back_process is launched and the parent send a httpresponse"""
        
    #we check if there is the GET parameter for research id
    research_id = -1
    if not "research_id" in request.GET:
        return HttpResponse(content="",status=400)
    else:
        research_id = request.GET["research_id"]

    #we check if the id exists in database
    research = Research.objects.filter(id=research_id)
    if not research.exists():
        return HttpResponse(content="This research doesn't exist",status=403)
    else:
        research = research[0]
    
    #we check if the research was already done
    if research.is_finish:
        return HttpResponse(content="This research was already done",status=403)

    #we check if the research is currently running
    if research.is_running:
        return HttpResponse(content="This research is already running",status=403)

    #we check if the user is the owner of this research
    #user = request.user
    #if not user == research.user:
    #    return HttpResponse(content="You don't own this research " + str(user.email) + " != " + str(research.user.email),status=403) 
    
    # when we make some multiprocessing, in django, we have to close all connections to database before
    from django import db
    db.connections.close_all()

    #we fork
    pid = os.fork()
    #parent process return httpresponse
    if pid > 0:
        pid = os.getpid()
        PID_Research.objects.create(research=research,pid=pid)
        back_process(research)
    # child process
    elif pid == 0:
        return HttpResponse(content="the research is running",status = 200)
    # if there is an error with forking, we return 500 error http
    else:
        return HttpResponse(content="Error with processing forking",status=500)

def check_process(request):
    """we get the id of a research and return true or false if the process is running or not"""
    #we check if there is the GET parameter for research id
    research_id = -1
    if not "research_id" in request.GET:
        return HttpResponse(content="",status=400)
    else:
        research_id = request.GET["research_id"]

    #we check if the id exists in database
    research = Research.objects.filter(id=research_id)
    if not research.exists():
        return HttpResponse(content="This research desn't exist",status=403)
    else:
        research = research[0]
    
    #we check if the research was already done
    if research.is_finish:
        return HttpResponse(content="This research was already done",status=403)

    #we check if the research is currently running
    if not research.is_running:
        return HttpResponse(content="This research isn't running",status=403)

    #we check if the user is the owner of this research
    #user = request.user
    #if not user == research.user:
    #    return HttpResponse(content="You don't own this research",status=403)
    
    #we check if we have the pid of the research
    pid = PID_Research.objects.filter(research=research)

    if not pid.exists():
        return HttpResponse(content="We don't have the pid of the process",status=500)
    else:
        pid = pid[0].pid
    
    #we check if the process is running
    is_running = True
    try:
        os.kill(pid,0)
        is_running = True
    except:
        is_running = False

    return_data = json.dumps({"is_running":is_running})
    return HttpResponse(content=return_data,status=200)


def delete_process(request):
    """We get the id of a research and we delete it"""
    # the user can stop and delete the process who is running

    #we check if there is the GET parameter for research id
    research_id = -1
    if not "research_id" in request.GET:
        return HttpResponse(content="",status=400)
    else:
        research_id = request.GET["research_id"]

    #we check if the id exists in database
    research = Research.objects.filter(id=research_id)
    if not research.exists():
        return HttpResponse(content="This research desn't exist",status=403)
    else:
        research = research[0]
    
    #we check if the research was already done
    if research.is_finish:
        return HttpResponse(content="This research was already done",status=403)

    #we check if the research is currently running
    if not research.is_running:
        return HttpResponse(content="This research isn't running",status=403)

    #we check if the user is the owner of this research
    #user = request.user
    #if not user == research.user:
    #    return HttpResponse(content="You don't own this research",status=403)
    
    #we check if we have the pid of the research
    pid = PID_Research.objects.filter(research=research)

    if not pid.exists():
        return HttpResponse(content="We don't have the pid of the process",status=500)
    else:
        pid = pid[0].pid
    
    #we send the signal to the process
    os.kill(int(pid), signal.SIGTERM)

    #we delete in the database
    Research.objects.filter(id=research_id).delete()

    #we delete the pdf in "BackEnd/functions/download if exist "
    for file in glob(f'BackEnd/functions/download/research_{research_id}*'):
        os.remove(file)
    
    #we delete all intermediate file in "BackEnd/data"
    for file in glob(f'BackEnd/data/*research_{research_id}*'):
        os.remove(file)

    return HttpResponse(contents='',status_code=200)

#we launch a thread as daemon for the method "relaunch_if_fault" so if there are some research with fault,
# it will automatically restart it and assign it a new pid
# only if the role is Backend

from programmeDjango.settings import IS_BACKEND

if IS_BACKEND:
    t = Thread(target=relaunch_if_fault,args={})
    t.setDaemon(True)
    t.start()

    u = Thread(target=update_research,args={})
    u.setDaemon(True)
    u.start()