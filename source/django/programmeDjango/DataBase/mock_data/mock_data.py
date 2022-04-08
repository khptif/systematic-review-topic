from UI_Front.models import *
from UI_Front.mock_data.data import article
from datetime import date

# add some mock data in Database for testing UI_Front fonctions

# create test user
try:
    test_user = CustomUser.objects.create(email="test@user.com",password="1234")
    print("user created")
except:
    test_user = CustomUser.objects.get(email="test@user.com")
    pass

# create test_request
test_request = Request.objects.create(type='research',user=test_user)
print("request created")
# create test_research
test_research = []
test_research.append( Research.objects.create(request=test_request,search='vih, africa',year_begin = date(1995,1,1),year_end = date(1999,1,1)))
test_research.append( Research.objects.create(request=test_request,search='vih, usa, "new york"',year_begin = date(1995,1,1),year_end = date(1999,1,1)))

print("research created")
# keywords of the research
words = []
words.append(['vih','africa'])
words.append(['vih', 'usa', '"new york"'])

for w in words[0]:
    Keyword.objects.create(word=w,research=test_research[0])
for w in words[1]:
    Keyword.objects.create(word=w,research=test_research[1])
print("keywords created")
# the articles

for _,art in article.items():
    # create the article
    article_object = Article.objects.create(title = art['title'], 
                            abstract = art['abstract'],
                            full_text = art['full_text'],
                            url_file=art['URL'],
                            publication=art['date'],
                            pmcid = art['pmcid'])

    # create the authors 
    authors = art['authors']
    for last_name,first_name in authors:
        a = Author.objects.create(last_name=last_name,first_name=first_name)
        # link author to the article
        Article_Author(article=article_object,author=a)
    
    #create the cluster data for the article
    Cluster.objects.create(research=test_research[0],
                            article=article_object,
                            topic=art['cluster'][0],
                            pos_x = art['cluster'][1],
                            pos_y = art['cluster'][2])

    #link the article to the research
    Research_Article.objects.create(article=article_object,research=test_research[0])
