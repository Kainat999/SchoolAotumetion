# Generated by Django 3.1.1 on 2024-05-01 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel_app', '0002_assessment_option_question_useranswer'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='obt_marks',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='assessment',
            name='total_marks',
            field=models.IntegerField(default=10),
        ),
    ]
