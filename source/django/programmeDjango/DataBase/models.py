from django.db import models
from UI_Front.models import CustomUser
import datetime
from django.utils import timezone



class Author(models.Model):
    last_name = models.CharField(max_length=128,null=True)
    first_name = models.CharField(max_length=128,null=True)

class Article(models.Model):
    title = models.CharField(max_length=1024,default='')
    doi = models.CharField(max_length=1024, default='')
    author = models.ManyToManyField(Author, through='Article_Author')
    abstract = models.TextField(default='')
    full_text = models.TextField(default='')
    publication = models.DateField(default=datetime.date(1900,1,1))
    url_file = models.URLField(max_length=4096,null=True)
    is_file_get = models.BooleanField(default=False)

class Article_Author(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class Research(models.Model):

    
    user = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True)
    articles = models.ManyToManyField(Article, through='Research_Article')
    search = models.CharField(max_length=256)
    year_begin = models.DateField(default=datetime.date(1900,1,1))
    year_end = models.DateField(default=datetime.date(1900,1,1))
    step = models.CharField(max_length=256,default='article')
    is_finish = models.BooleanField(default=False)
    is_running = models.BooleanField(default=False)
    is_error = models.BooleanField(default=False)
    error = models.CharField(max_length=256,default='')
    max_article = models.IntegerField(default=0)
    best_dbcv = models.FloatField(default=0.0)

    process_time = models.IntegerField(default=0)
    current_article_db = models.CharField(max_length=128,default='')
    begining_date = models.DateField(null=True)

class Research_Article(models.Model):
    research = models.ForeignKey(Research,on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

class Keyword(models.Model):
    word = models.CharField(max_length=128)
    research = models.ForeignKey(Research,on_delete=models.CASCADE)


class Cluster(models.Model):
    research = models.ForeignKey(Research, on_delete=models.CASCADE)
    topic = models.CharField(max_length=8196)
    pos_x = models.IntegerField()
    pos_y = models.IntegerField()
    article = models.ForeignKey(Article,on_delete=models.CASCADE)

class TableChoice(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    research = models.ForeignKey(Research,on_delete=models.CASCADE)
    article = models.ForeignKey(Article,on_delete=models.CASCADE)
    to_display = models.BooleanField(default=True)
    is_initial = models.BooleanField(default=True)
    is_check = models.BooleanField(default=False)

class ThreadDaemon(models.Model):
    name = models.CharField(max_length=128)
    is_running = models.BooleanField(default=False)
    check_still_running = models.IntegerField(default=0)