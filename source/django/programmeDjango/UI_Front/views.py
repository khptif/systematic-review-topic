from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout

from UI_Front.forms import *
from UI_Front.models import CustomUser

@login_required(login_url='/login')
def page_accueil(request):

    return render(request,'page_accueil.html')


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

# Create your views here.
