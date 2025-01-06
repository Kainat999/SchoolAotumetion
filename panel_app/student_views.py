import json
import math
from datetime import datetime
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *


def student_home(request):
    student = get_object_or_404(Student, admin=request.user)
    total_subject = Subject.objects.filter(course=student.course).count()
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    subject_name = []
    data_present = []
    data_absent = []
    subjects = Subject.objects.filter(course=student.course)
    for subject in subjects:
        attendance = Attendance.objects.filter(subject=subject)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, student=student).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, student=student).count()
        subject_name.append(subject.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_subject': total_subject,
        'subjects': subjects,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': subject_name,
        'page_title': 'Student Homepage'

    }
    return render(request, 'student_template/home_content.html', context)


@ csrf_exempt
def student_view_attendance(request):
    student = get_object_or_404(Student, admin=request.user)
    if request.method != 'POST':
        course = get_object_or_404(Course, id=student.course.id)
        context = {
            'subjects': Subject.objects.filter(course=course),
            'page_title': 'View Attendance'
        }
        return render(request, 'student_template/student_view_attendance.html', context)
    else:
        subject_id = request.POST.get('subject')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), subject=subject)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


def student_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Student Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('student_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    student = get_object_or_404(Student, admin=request.user)
    form = StudentEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = student.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "student_template/student_view_profile.html", context)




@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request):
    student = get_object_or_404(Student, admin=request.user)
    notifications = NotificationStudent.objects.filter(student=student)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student)
    context = {
        'results': results,
        'page_title': "View Results"
    }
    return render(request, "student_template/student_view_result.html", context)




# Assessments:


@login_required
def assessment_list(request):
    assessments = Assessment.objects.all()
    assessment_types_colors = {
        'quiz': 'orange-btn',
        'exam': 'red-btn',
        'assignment': 'blue-btn',
        
    }

    return render(request, 'student_template/assessment_list.html', {
        'assessments': assessments,
        'assessment_types_colors': assessment_types_colors,
    })

@login_required
def assessment_detail(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    questions = assessment.question_set.all()
    admin = request.user
    student = Student.objects.get(admin=admin)
    
    user_answers = UserAnswer.objects.filter(user=student, question__in=questions)
    has_taken_assessment = user_answers.exists()

    user_assignment = UserAnswer.objects.filter(assessment=assessment, user=student, answer_file__isnull=False).first()

    if request.user.is_superuser and request.method == "POST":
        for answer in user_answers:
            is_correct = request.POST.get(f'is_correct_for_{answer.id}')
            answer.is_correct = True if is_correct == "correct" else False
            answer.save()
        return redirect('stu_assessment_detail', assessment_id=assessment_id)

    questions_with_options = [{
        'question': question,
        'options': question.option_set.all()
    } for question in questions]

    return render(request, 'student_template/assessment_detail.html', {
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
                        user=Student.objects.get(admin=request.user),
                        assessment=assessment,
                        question=question,
                        answer_file=file
                    )
                else:
                    messages.error(request, "You forgot to upload a file for one or more questions.")
                    return redirect('stu_assessment_detail', assessment_id=assessment.id)

            elif assessment.type == 'quiz':
                selected_option_id = request.POST.get(f'answer_for_{question.id}')
                
                if not selected_option_id:
                    messages.error(request, "You missed answering a question. Please make sure to select an option for all questions.")
                    return redirect('stu_assessment_detail', assessment_id=assessment.id)
                
                try:
                    selected_option = Option.objects.get(id=selected_option_id)
                    is_correct = selected_option.is_correct
                    
                    UserAnswer.objects.create(
                        user=Student.objects.get(admin=request.user),
                        assessment=assessment,
                        question=question,
                        answer=selected_option.text,
                        is_correct=is_correct
                    )

                    if not is_correct:
                        all_answers_correct = False
                        messages.warning(request, f"Your answer for '{question.text}' is not correct. Please try again.")
                        
                        user_answer = UserAnswer.objects.get(user=Student.objects.get(admin=request.user), question=question)
                        user_answer.delete()
                        return redirect('stu_assessment_detail', assessment_id=assessment.id)

                except Option.DoesNotExist:
                    messages.error(request, "There was an error with your submission. Please try again.")
                    return redirect('stu_assessment_detail', assessment_id=assessment.id)

            elif assessment.type == 'exam':
                text_answer = request.POST.get(f'text_answer_for_{question.id}')
                
                if text_answer:
                    UserAnswer.objects.create(
                        user=Student.objects.get(admin=request.user),
                        assessment=assessment,
                        question=question,
                        answer=text_answer
                    )
                else:
                    messages.error(request, "You missed answering a question. Please make sure to provide an answer for all questions.")
                    return redirect('stu_assessment_detail', assessment_id=assessment.id)

        if all_answers_correct:
            messages.success(request, "Congratulations! You answered all questions correctly.")
            return redirect('stu_assessment_detail', assessment_id=assessment.id)
        elif assessment.type == 'exam':
            messages.info(request, "Quiz submitted! Check below for your results.")
            return redirect('stu_assessment_detail', assessment_id=assessment.id)

    return render(request, 'student_template/assessment_detail.html', {
        'assessment': assessment,
        'questions': incorrect_questions if incorrect_questions else questions
    })


