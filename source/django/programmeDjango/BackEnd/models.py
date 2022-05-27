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


# Create your models here.
