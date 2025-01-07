from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.assessment_list, name='assessment_list'),
    path('as/<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    path('as/<int:assessment_id>/take/', views.assessment_take, name='assessment_take'),
    path('as/', views.assessment_Tlist, name='assessment_Tlist'),
    path('new/', views.create_edit_assessment, name='create_edit_assessment'),
    path('as<int:assessment_id>/edit/', views.create_edit_assessment, name='edit_assessment'),
    path('as<int:assessment_id>/submissions/', views.view_user_answers, name='view_user_answers'),
    path('as/<int:assessment_id>/add_question/', views.add_question, name='add_question'),
    path('question/<int:question_id>/add_option/', views.add_option, name='add_option'),


]