# Generated by Django 3.1.1 on 2025-01-06 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assesments', '0003_auto_20250106_0704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswer',
            name='is_correct',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]