from django import forms
from .models import Assessment, Question, UserAnswer, Option

class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['name', 'type']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = UserAnswer
        fields = ['answer']
       


# teacher assessments


class AssessmentTForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['name', 'type', 'keywords', 'difficulty_level']

class QuestionTForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['assessment', 'text']

class OptionTForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['question', 'text', 'is_correct']

class UserAnswerTForm(forms.ModelForm):
    class Meta:
        model = UserAnswer
        fields = ['user', 'assessment', 'question', 'answer', 'is_correct', 'answer_file']


