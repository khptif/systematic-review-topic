# Generated by Django 4.0.4 on 2022-05-20 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0006_research_is_running_research_max_article'),
        ('BackEnd', '0003_preprocess_text_research'),
    ]

    operations = [
        migrations.CreateModel(
            name='PID_Research',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.IntegerField()),
                ('research', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DataBase.research')),
            ],
        ),
    ]