from django.db import models

class Assessment(models.Model):
    ASSESSMENT_TYPES = (
        ('quiz', 'Quiz'),
        ('exam', 'Exam'),
        ('assignment', 'Assignment'),
    )
    name = models.CharField(max_length=255)
    type = models.CharField(choices=ASSESSMENT_TYPES, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords related to the assessment.")
    difficulty_level = models.CharField(
        max_length=20,
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        default=1 
    )
class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    text = models.TextField()

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(null=True, blank=True, default=None)

from django.conf import settings

class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="user_answers", null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=1000) 
    timestamp = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(null=True, blank=True)
    answer_file = models.FileField(upload_to='user_submissions/', null=True, blank=True)
