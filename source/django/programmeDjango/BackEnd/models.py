from django.db import models
from DataBase.models import Research

class Preprocess_text(models.Model):
    research = models.ForeignKey(Research,on_delete=models.CASCADE,null=True)
    id_article = models.IntegerField()
    text = models.TextField()

class Number_trial(models.Model):
    research = models.ForeignKey(Research,on_delete=models.CASCADE)

class Number_preprocess(models.Model):
    research = models.ForeignKey(Research,on_delete=models.CASCADE)

class Article_Step(models.Model):
    research = models.ForeignKey(Research,on_delete=models.CASCADE)
    step = models.TextField()

class Article_Job(models.Model):
    research = models.ForeignKey(Research,on_delete=models.CASCADE)
    job = models.TextField()
    type = models.TextField()


# Create your models here.
