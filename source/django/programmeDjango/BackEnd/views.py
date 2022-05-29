from django.http import HttpResponse

from BackEnd.functions.view_functions import *

#we launch a thread as daemon for the method "relaunch_if_fault" so if there are some research with fault,
# it will automatically restart it 

t = Thread(target=relaunch_if_fault,args={})
t.setDaemon(True)
t.start()

u = Thread(target=update_research,args={})
u.setDaemon(True)
u.start()