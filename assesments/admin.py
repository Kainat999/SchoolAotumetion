from django.contrib import admin
from .models import Assessment, Question, Option, UserAnswer

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'created_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'assessment')


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:  
            return []
        return ['is_correct']  


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'assessment', 'question', 'answer', 'timestamp', 'is_correct')

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ['is_correct']  
