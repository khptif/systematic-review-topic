# Generated by Django 4.0.4 on 2022-05-27 22:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0009_research_best_dbcv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='abstract',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='article',
            name='full_text',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='article',
            name='publication',
            field=models.DateField(default=datetime.date(1900, 1, 1)),
        ),
        migrations.AlterField(
            model_name='author',
            name='first_name',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='last_name',
            field=models.CharField(max_length=128, null=True),
        ),
    ]