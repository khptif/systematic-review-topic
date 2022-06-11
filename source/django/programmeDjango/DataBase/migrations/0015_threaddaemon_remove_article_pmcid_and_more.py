# Generated by Django 4.0.4 on 2022-06-06 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0014_tablechoice_is_check_delete_article_temporary'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreadDaemon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('is_running', models.BooleanField(default=False)),
                ('check_still_running', models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='article',
            name='pmcid',
        ),
        migrations.AddField(
            model_name='research',
            name='begining_date',
            field=models.DateField(null=True),
        ),
    ]