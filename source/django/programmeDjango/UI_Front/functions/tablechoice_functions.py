from UI_Front.functions.utils_functions import *
from DataBase.models import *
from DataBase.functions.view_functions import *
from django.http.response import HttpResponse


def update_new_TableChoice(user,research,article_id_list):
    """When user make a new research filtering, the ancients are deleted and the new are written"""
    #we remove all row with this user
    TableChoice.objects.filter(user=user).delete()
    # we add new rows
    for id in article_id_list :
        TableChoice.objects.create(user=user,research=research,article=Article.objects.get(id=id))
    
def update_neighbour_TableChoice(user,research):
    """With an initial list of article from all row who are to_display True, we add the nearest neighbour of these article in table choice."""
    tablechoice = TableChoice.objects.filter(user=user,research=research,to_display=True)
    for row in tablechoice:

        neighbours = neighbour_article(row.article,research)
        # we add these article. We check if the article is already in a row
        for article in neighbours:
            if TableChoice.objects.filter(user=user,research=research, article=article).exists():
                continue
            else:
                TableChoice.objects.create(user=user,research=research,article=article,is_initial=False)

def update_article_to_display_TableChoice(user,research,list_id):
    """The function take a list of id object of TableChoice row and user. All row who is not in list_id,
    the boolean 'to_display' will be put to False. The function take user id by security. We check if all id
    in 'list_id' is owned by user because, the list of id come from the front-end by the user """

    # we check the ownership of the user for row in TableChoice
    for id in list_id:
        test = TableChoice.objects.get(id=id)
        if not test.user == user:
            return False

    #we update the boolean 'to_display' if the article is in the list or is checked, put to True
    tablechoice = TableChoice.objects.filter(user=user,research=research,to_display=True)
    for row in tablechoice:
        # if the article is not in the check list, not to display
        if not str(row.id) in list_id and not row.is_check :
            row.to_display = False
            row.save()
    
def update_article_is_check_TableChoice(user,research,list_id):
    """The function take a list of id object of TableChoice row and user. All row who is in list_id,
    the boolean 'is_check' will be put to True. The function take user id by security. We check if all id
    in 'list_id' is owned by user because, the list of id come from the front-end by the user """

    # we check the ownership of the user for row in TableChoice
    for id in list_id:
        test = TableChoice.objects.get(id=id)
        if not test.user == user:
            return False

    #we update the boolean 'to_display' and the boolean "is_checked"
    tablechoice = TableChoice.objects.filter(user=user,research=research,to_display=True)
    for row in tablechoice:
        # if the article is  in the check list, keep the checkbox checked
        if str(row.id) in list_id:
            row.is_check = True
            row.save()

def all_display_TableChoice(user,research):
    """ Reset all article so we can display all article"""    
    tablechoice = TableChoice.objects.filter(user=user,research=research)
    for row in tablechoice:
        row.to_display = True

def reset_TableChoice(user,research):
    """ To reset, we delete all row who have been added and put to_display to true """
    TableChoice.objects.filter(user=user,research=research,is_initial=False).delete()
    for tablechoice in TableChoice.objects.filter(user=user,research=research):
        tablechoice.to_display=True
        tablechoice.is_check=False
        tablechoice.save()

def download_finalzip(research,user):
    
    from programmeDjango.settings import is_decentralized
    if is_decentralized:
        from remote_functions import get_final_zip_remote
        fichier_zip = get_final_zip_remote(research,user)
        if not fichier_zip == False:
            return fichier_zip
    else:
        filepath = create_final_file(research,user)
        # Open the file for reading content
        path = open(filepath, 'rb')
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type="application/zip")
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename={name_file}".format(name_file="final_articles.zip")
        # Return the response value
        return response