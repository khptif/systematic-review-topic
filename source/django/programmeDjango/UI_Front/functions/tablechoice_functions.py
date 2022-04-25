from UI_Front.functions.utils_functions import *
from DataBase.models import *

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

    #we update the boolean 'to_display'
    tablechoice = TableChoice.objects.filter(user=user,research=research,to_display=True)
    for row in tablechoice:
        if not str(row.id) in list_id:
            row.to_display = False
            row.save()
    


def all_display_TableChoice(user,research):
    """ Reset all article so we can display all article"""    
    tablechoice = TableChoice.objects.filter(user=user,research=research)
    for row in tablechoice:
        row.to_display = True

def reset_TableChoice(user,research):
    """ To reset, we delete all row who have been added and put to_display to true """
    TableChoice.objects.filter(user=user,research=research,is_initial=False).delete()
    for tablechoice in TableChoice.objects.filter(user=user,research=research,to_display=False):
        tablechoice.to_display=True
        tablechoice.save()

def test_download_finalzip(request,user,research):
    from zipfile import ZipFile
    import os
    import os.path
    from django.http.response import HttpResponse
    import mimetypes
    import tarfile

    liste_article = Article.objects.filter(tablechoice__user = user,tablechoice__research=research,tablechoice__to_display=True)
    user_name = user.email[:6]
    filename = 'final_'+user_name+'.tar'
    if os.path.exists(filename):
        os.remove(filename)
    
    zipfinal = ZipFile('final.zip', 'w')
    tarfinal = tarfile.open(filename,'w')
    
    for article in liste_article:
        title = article.title
        if len(title) > 30:
            title = title[:31]
        elif len(title) <= 0:
            title = 'no_title'
        title += '.txt'
        full_text = article.full_text
        try:
            file = open(title,'w')
        except:
            file.close()
            continue
        
        file.write(full_text)
        file.close()
        zipfinal.write(title)
        tarfinal.add(title)
        os.remove(title)
    zipfinal.close()
    tarfinal.close()
    
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Define text file name
    
    # Define the full file path
    filepath = BASE_DIR + '/' + filename
    # Open the file for reading content
    path = open(filepath, 'r',encoding="utf-8", errors="ignore")
    # Set the mime type
    mime_type, _ = mimetypes.guess_type(filepath)
    # Set the return value of the HttpResponse
    response = HttpResponse(path, content_type=mime_type)
    # Set the HTTP header for sending to browser
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # Return the response value
    return response