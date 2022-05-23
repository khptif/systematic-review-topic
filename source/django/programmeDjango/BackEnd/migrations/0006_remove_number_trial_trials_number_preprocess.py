# Generated by Django 4.0.4 on 2022-05-22 15:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DataBase', '0008_alter_research_year_begin_alter_research_year_end'),
        ('BackEnd', '0005_number_trial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='number_trial',
            name='trials',
        ),
        migrations.CreateModel(
            name='Number_preprocess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('research', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DataBase.research')),
            ],
        ),
    ]