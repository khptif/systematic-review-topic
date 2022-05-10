from django.shortcuts import render
from BackEnd.functions.Get_arXiV import Get_arXiV
from BackEnd.functions.Get_biorXiv import Get_biorXiv
from BackEnd.functions.Get_medrXiv import Get_medrXiv


# Create your views here.

def research ():
    search = "vih"
    print("execute arxiv")
    #Get_arXiV(search,"arx")
    print("execute bio")
    Get_biorXiv(search,"bio")
    print("execute med")
    #Get_medrXiv(search,"med")


