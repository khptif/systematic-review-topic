# Generated by Django 4.0.4 on 2022-05-16 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0004_alter_article_doi_alter_article_title'),
        ('BackEnd', '0002_step_processus'),
    ]

    operations = [
        migrations.AddField(
            model_name='preprocess_text',
            name='research',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='DataBase.research'),
        ),
    ]