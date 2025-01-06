# Generated by Django 3.1.1 on 2024-05-01 05:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('panel_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('quiz', 'Quiz'), ('exam', 'Exam'), ('assignment', 'Assignment')], max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(default='0', on_delete=django.db.models.deletion.CASCADE, to='panel_app.course')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panel_app.assessment')),
            ],
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=1000)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_correct', models.BooleanField(default=False)),
                ('answer_file', models.FileField(blank=True, null=True, upload_to='user_submissions/')),
                ('assessment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_answers', to='panel_app.assessment')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panel_app.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panel_app.student')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('is_correct', models.BooleanField(blank=True, default=None, null=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='panel_app.question')),
            ],
        ),
    ]
