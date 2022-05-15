from django.db import models
from DataBase.models import Research

class step_processus(models.Model):
    research = models.ForeignKey(Research,on_delete=models.CASCADE)
    step = models.CharField(max_length=128)

class preprocess_text(models.Model):
    id_article = models.IntegerField()
    text = models.TextField()

# Create your models here.
