"""
URL configuration for projekt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from app1 import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('profile/', views.myProfile, name="myProfile"),
    path('error/', views.error, name="error"),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.register, name='register'),

    path('menu/student/', views.studentDashboard, name='menu_student'),
    path('menu/student/enroll_subject/<int:subject_id>/', views.enrollSubject, name='enroll_subject'),
    path('menu/student/unenroll_subject/<int:subject_id>/', views.unenrollSubject, name='unenroll_subject'),
    path('menu/student/filter_subjects/', views.filterSubjects, name='filter_subjects'),

    path('menu/professor/', views.professorDashboard, name='menu_professor'),
    path('menu/professor/subjects/', views.professorSubjects, name='professor_subjects'),
    path('menu/professor/subjects/students/<int:subject_id>/', views.viewStudents, name='view_students'),
    path('menu/professor/subjects/students/failed_to_pass/<int:subject_id>/', views.viewStudentsFailed, name='view_students_failed'),
    path('menu/professor/subjects/students/enrolled/<int:subject_id>/', views.viewStudentsEnrolled, name='view_students_enrolled'),
    path('menu/professor/subjects/students/passed/<int:subject_id>/', views.viewStudentsPassed, name='view_students_passed'),

    path('menu/admin/', views.AdminDashboard, name='menu_admin'),
    path('menu/admin/subjects/', views.subjectAdmin, name='subjects_list'),
    path('menu/admin/subjects/update/<int:subject_id>/', views.subjectUpdate, name='subject_update'),
    path('menu/admin/subjects/add/', views.subjectAdd, name='add_subject'),
    path('menu/admin/subjects/students/<int:subject_id>/', views.studentsSubject, name='students_subject'),

    path('menu/admin/subjects/enrollment_form/<int:student_id>/', views.enrollmentFormAdmin, name='enrollment_form'),
    path('menu/admin/subjects/enrollment_form/<int:student_id>/enroll_subject_admin/<int:subject_id>/', views.enrollSubjectAdmin, name='enroll_subject_admin'),
    path('menu/admin/subjects/enrollment_form/<int:student_id>/unenroll_subject_admin/<int:subject_id>/', views.unenrollSubjectAdmin, name='unenroll_subject_admin'),
    path('menu/admin/students/v/<int:student_id>/', views.enrollmentFormAdmin, name='enrollment_form'),

    path('menu/admin/students/', views.studentAdmin, name='students_list'),
    path('menu/admin/students/update/<int:student_id>/', views.studentUpdate, name='student_update'),
    path('menu/admin/students/add/', views.studentAdd, name='add_student'),

    path('menu/admin/professors/', views.professorAdmin, name='professors_list'),
    path('menu/admin/professors/update/<int:professor_id>/', views.professorUpdate, name='professor_update'),
    path('menu/admin/professors/add/', views.professorAdd, name='add_professor'),
]