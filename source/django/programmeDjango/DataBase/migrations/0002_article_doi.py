# Generated by Django 3.2 on 2022-04-10 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='doi',
            field=models.CharField(default='', max_length=256),
        ),
    ]
