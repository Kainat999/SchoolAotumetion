

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Assessment, UserAnswer, Option, Question
from django.contrib import messages
from .forms import AssessmentTForm, OptionTForm, QuestionTForm, UserAnswerTForm



@login_required
def assessment_list(request):
    assessments = Assessment.objects.all()
    assessment_types_colors = {
        'quiz': 'orange-btn',
        'exam': 'red-btn',
        'assignment': 'blue-btn',
        
    }

    return render(request, 'assessment_list.html', {
        'assessments': assessments,
        'assessment_types_colors': assessment_types_colors,
    })

@login_required
def assessment_detail(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = assessment.question_set.all()
    user_answers = UserAnswer.objects.filter(user=request.user, question__in=questions)
    has_taken_assessment = user_answers.exists()

    user_assignment = UserAnswer.objects.filter(assessment=assessment, user=request.user, answer_file__isnull=False).first()

    if request.user.is_superuser and request.method == "POST":
        for answer in user_answers:
            is_correct = request.POST.get(f'is_correct_for_{answer.id}')
            answer.is_correct = True if is_correct == "correct" else False
            answer.save()
        return redirect('assessment_detail', assessment_id=assessment_id)

    questions_with_options = [{
        'question': question,
        'options': question.option_set.all()
    } for question in questions]

    return render(request, 'assessment_detail.html', {
        'assessment': assessment,
        'questions_with_options': questions_with_options,
        'user_answers': user_answers,
        'has_taken_assessment': has_taken_assessment,
        'user_assignment': user_assignment
    })








@login_required
def assessment_take(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = assessment.question_set.all()
    incorrect_questions = []

    if request.method == "POST":
        all_answers_correct = True

        for question in questions:
            if assessment.type == 'assignment':
                file = request.FILES.get(f'file_for_{question.id}')
                if file:
                    UserAnswer.objects.create(
                        user=request.user,
                        assessment=assessment,
                        question=question,
                        answer_file=file,
                        is_correct=None
                    )
                else:
                    messages.error(request, "You forgot to upload a file for one or more questions.")
                    return redirect('assessment_detail', assessment_id=assessment.id)

            elif assessment.type == 'quiz':
                selected_option_id = request.POST.get(f'answer_for_{question.id}')
                
                if not selected_option_id:
                    messages.error(request, "You missed answering a question. Please make sure to select an option for all questions.")
                    return redirect('assessment_detail', assessment_id=assessment.id)
                
                try:
                    selected_option = Option.objects.get(id=selected_option_id)
                    is_correct = selected_option.is_correct
                    
                    UserAnswer.objects.create(
                        user=request.user,
                        assessment=assessment,
                        question=question,
                        answer=selected_option.text,
                        is_correct=is_correct
                    )

                    if not is_correct:
                        all_answers_correct = False
                        messages.warning(request, f"Your answer for '{question.text}' is not correct. Please try again.")
                        
                        user_answer = UserAnswer.objects.get(user=request.user, question=question)
                        user_answer.delete()
                        return redirect('assessment_detail', assessment_id=assessment.id)

                except Option.DoesNotExist:
                    messages.error(request, "There was an error with your submission. Please try again.")
                    return redirect('assessment_detail', assessment_id=assessment.id)

            elif assessment.type == 'exam':
                text_answer = request.POST.get(f'text_answer_for_{question.id}')
                
                if text_answer:
                    UserAnswer.objects.create(
                        user=request.user,
                        assessment=assessment,
                        question=question,
                        answer=text_answer,
                        is_correct=None
                    )
                else:
                    messages.error(request, "You missed answering a question. Please make sure to provide an answer for all questions.")
                    return redirect('assessment_detail', assessment_id=assessment.id)

        if all_answers_correct:
            messages.success(request, "Congratulations! You answered all questions correctly.")
            return redirect('assessment_detail', assessment_id=assessment.id)
        elif assessment.type == 'exam':
            messages.info(request, "Quiz submitted! Check below for your results.")
            return redirect('assessment_detail', assessment_id=assessment.id)

    return render(request, 'assessment_detail.html', {
        'assessment': assessment,
        'questions': incorrect_questions if incorrect_questions else questions
    })




# Teacher side :


# List all assessments
@login_required
def assessment_Tlist(request):
    assessments = Assessment.objects.all()
    return render(request, 'assessment_Tlist.html', {'assessments': assessments})

# Create or edit an assessment
@login_required
def create_edit_assessment(request, assessment_id=None):
    if assessment_id:
        assessment = get_object_or_404(Assessment, id=assessment_id)
        action = "Edit"
    else:
        assessment = None
        action = "Create"

    if request.method == "POST":
        form = AssessmentTForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Assessment {action.lower()}ed successfully!")
            return redirect('edit_assessment', assessment_id=form.instance.id)
    else:
        form = AssessmentTForm(instance=assessment)

    questions = assessment.question_set.all() if assessment else None

    return render(request, 'create_edit_assessment.html', {
        'form': form,
        'action': action,
        'assessment': assessment,
        'questions': questions,
    })

# Add a question to an assessment
@login_required
def add_question(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    if request.method == "POST":
        form = QuestionTForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Question added successfully!")
            return redirect('edit_assessment', assessment_id=assessment.id)
    else:
        form = QuestionTForm(initial={'assessment': assessment})

    return render(request, 'add_question.html', {'form': form, 'assessment': assessment})

# Add an option to a question
@login_required
def add_option(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == "POST":
        form = OptionTForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Option added successfully!")
            return redirect('edit_assessment', assessment_id=question.assessment.id)
    else:
        form = OptionTForm(initial={'question': question})
    return render(request, 'add_option.html', {'form': form, 'question': question})



@login_required
def view_user_answers(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    user_answers = UserAnswer.objects.filter(assessment=assessment)

    if request.method == "POST":
        for answer in user_answers:
            is_correct = request.POST.get(f'is_correct_for_{answer.id}')
            if is_correct is not None:
                answer.is_correct = True if is_correct == 'correct' else False
                answer.save()

        messages.success(request, "Answers updated successfully!")
        return redirect('view_user_answers', assessment_id=assessment.id)

    return render(request, 'view_user_answers.html', {'assessment': assessment, 'user_answers': user_answers})


