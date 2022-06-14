
from DataBase.models import *
import zipfile
from programmeDjango.settings import TEMPORARY_DATA,ARTICLE_DATA
import glob
import os

def create_final_file(research,user):
    #we create a zip file with all article checked in TableChoice
    #and return the name of the file

    #we create the zip file
    path_zip = TEMPORARY_DATA + "/research_{id}_final.zip".format(id=str(research.id))
    zip_file = zipfile.ZipFile(path_zip,mode="w")
    
    #we get the articles
    list_tablechoice = TableChoice.objects.filter(research=research,user=user,is_check=True)
    # for each article, we will put in the directory that represent his own cluster
   
    for row in list_tablechoice:

        article = row.article
        #we get the cluster object of this research and article
        cluster = Cluster.objects.filter(research=research,article=article)
        #we check if exist
        if not cluster.exists():
            continue
        else:
            cluster = cluster[0]
        
        #we get the file to the article
        files = glob.glob(ARTICLE_DATA + "/article_{id}_*.pdf".format(id=str(article.id)))

        file_exist = False
        #we check if the pdf article exists
        if len(files) > 0:
            #we get his pathname
            path_to_article = os.path.abspath(files[0])
            file_exist = True

        else:
            path_to_article = TEMPORARY_DATA + "/research_{id_research}_user_{id_user}_article_{id_article}.txt".format(id_research = research.id,id_user = user.id,id_article = article.id)
            #we create a little file .txt with information about the article
            f = open(path_to_article,mode="w")

            try:
                #we write the title, doi, url, author and abstract
                f.write(article.title + "\n\n")
                if article.doi is None:
                    article.doi = ""
                f.write("DOI: " + article.doi + "\n\n")
                if article.url_file is None:
                    article.url_file = ""
                f.write("URL: " + article.url_file + "\n\n")

                author_string = ""
                for author in Author.objects.filter(article_author__article = article):
                    author_string += author.last_name + " " + author.first_name + ";\n"

                f.write("Authors: \n" + author_string + "\n\n")
                f.write("Abstract \n" + article.abstract)
            finally:
                f.close()

        #we add the article to the zip file
        topic = cluster.topic.replace(" ","").replace(",","_")
        if len(topic) > 128:
            topic = topic[0:128]
        
        file_name = article.title.replace(" ","_")
        if len(file_name) > 128:
            file_name = file_name[0:128]
        
        if file_exist:
            file_name += ".pdf"
        else:
            file_name += ".txt"
            
        zip_file.write(path_to_article,"{topic}/{file_name}".format(topic=topic,file_name=file_name))
    
    zip_file.close()
    # we delete all temporary file
    files_delete = glob.glob(TEMPORARY_DATA + "/research_{id_research}_user_{id_user}_article_*.txt".format(id_research = research.id,id_user = user.id))
    for f in files_delete:
        #we check if exist before
        os.remove(f)
    
    return path_zip