from dataclasses import replace
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
import re

from .models import CustomUser
from DataBase.models import *

class SignForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("email already exist")
        else:
            return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        data = super(LoginForm,self).clean()
        email = data['email']
        if not CustomUser.objects.filter(email=email).exists():
            raise ValidationError("email doesn't exist")
        else:
            return data

    def clean_password(self):
        data = super(LoginForm,self).clean()
        email = data['email']
        password = data['password']
        check = authenticate(email=email,password=password)
        if check is None:
            raise ValidationError("incorrect password")
        else:
            return password

def errorParsingResearch(string_to_parse):
    """ Check if there is error in the search string for the research"""
    lower_string = string_to_parse.lower()
    char=re.findall("(?![a-z]|\(|\)|[0-9]|\-|\"|,|;|\s).",lower_string)
    # check if there are forbidden characters. Only [a-z], [0-9], '-', double quotes, comma, ';' ,parenthesis and space allowed
    # if founded, return forbidden characters
    if char:
        forbidden_char = ""
        for c in char:
            forbidden_char += " ' " + c + " ' "
            forbidden_char += ' '
        return (False, "Forbidden characters : " + forbidden_char)

    # check if there are words
    words = re.findall("[a-z0-9\-]+",lower_string)
    if not words:
        return (False, " Error, there is no word")
    # check if the words are not only a single '-'
    keyword = False
    for w in words:
        if not w=='-':
            keyword = True
            break

    if not keyword:
        return (False, "Error, thers is no keyword")

    #check if for a opened quote there is a closed quote
    # we check if there is a even number of quotes
    quotes = re.findall("\"",lower_string)
    if not len(quotes)%2 == 0:
        return (False, "Error, it misses a quote")

    #check if between each keywords, there is a [ ',' ';' ',(' '),' ';(' ');']
    # it must not exist empty keywords between these characters
    number_keyword = 0
    quotes_keyword = re.findall("\"[a-z0-9\-\s]*\"",lower_string)
    number_keyword += len(quotes_keyword)
    s=lower_string
    for qw in quotes_keyword:
        s = s.replace(qw,"")
    single_keyword = re.findall("[a-z0-9\-]+",s)
    number_keyword += len(single_keyword)
    for sw in single_keyword:
        s = s.replace(sw,"")
    # we replace espace by empty character.
    s = s.replace(" ","")
    # now, it must exist (number_keyword -1) characters from [ ',' ';' ',(' '),' ';(' ');']
    # we extract the cases with parenthesis
    parenthesis = re.findall("[,;]{1}\(",s)
    s = s.replace(",(","")
    s = s.replace(";(","")
    
    p = re.findall("\)[,;]{1}",s)
    parenthesis.extend(p)
    # we delete parenthesis in string with their [',' ';'].
    for p in parenthesis:
        s = s.replace(p,"")
    #we recuperate the commas
    comma = re.findall("[,;]{1}",s)

    occurence = 0
    size = len(parenthesis) + len(comma)
    if not size == number_keyword - 1:
        if size < number_keyword - 1:
            return (False,"Error, it misses some comma")
        elif size > number_keyword -1:
            return (False, "Error, there are too comma") 
    
    #check if into quotes there are only [a-z0-9],'-' and space
    # we delete good quotes keywords and we check if there are still quote
    quotes_word = re.findall("\"[a-z0-9\-\s]*\"",lower_string)
    s = lower_string
    for qw in quotes_word:
        s = s.replace(qw,"")
    
    bad_quotes = re.findall("\"",s)
    if bad_quotes:
        return (False,"Error, one of the quotes keyword is bad")

    #check if between each keywords there is a 

        
    #check parenthesis. opened parenthesis must have a closed one and be before closed one.
    # During the parsing, for var n, '(' => +1, ')' => -1. If negative value, problem with ')'.
    # If negatif value, too many ')'. If not zero after parsing, too many '('
    n = 0
    for c in lower_string:
        if c == '(':
            n += 1
        elif c == ')':
            n -= 1

        if n < 0 :
            return (False, "Error with ' ) ', closed parenthesis")
        
    if not n == 0:
        return (False,"Error with ' ( ', opened parenthesis")

    # return True if pass all checks

    return (True,"")


class Research_form(forms.Form):
    search = forms.CharField(max_length=512)
    year_begin = forms.IntegerField(min_value=1990)
    year_end = forms.IntegerField(min_value=1990)

    def clean(self):
        data = super(Research_form,self).clean()
        year_begin = data['year_begin']
        year_end = data['year_end']
        if year_end < year_begin :
            raise ValidationError(" year_end must be higher or equal than year_begin")
        else:
            return data

    def clean_search(self):
        data = super(Research_form,self).clean()
        search = data['search']
        check , error = errorParsingResearch(search)
        if check:
            return search
        else:
            raise ValidationError(error)

def errorParsingHistorical(search_string):
    """ Check if there are errors in the string search for historical"""
    lower_string = search_string.lower()

    char=re.findall("(?![a-z0-9\-\"]| ).",lower_string)
    # check if there are forbidden characters. Only [a-z] and space allowed
    # if founded, return forbidden characters
    if char:
        forbidden_char = ''
        for c in char:
            forbidden_char += c
            forbidden_char += ' '
        return (False, "Forbidden characters : " + forbidden_char)

    # check if there are words
    quotes_words = re.findall("\"[a-z0-9\-\s]+\"",lower_string)
    s = lower_string
    for qw in quotes_words:
        s=s.replace(qw,"")
    single_words = re.findall("[a-z0-9\-]+",s)
    words = []
    words.extend(quotes_words)
    words.extend(single_words)

    if not words:
        return (False, " Error, there is no word")
    
    return (True,'')


class Historical_form(forms.Form):
    search = forms.CharField(max_length=1024)

    def clean_search(self):
        data = super(Historical_form,self).clean()
        search = data['search']
        check , error = errorParsingHistorical(search)
        if check:
            return search
        else:
            raise ValidationError(error)