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
from django.urls import path, include, re_path
from app1 import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('', views.home, name=''),   
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('profile/', views.myProfile, name="myProfile"),
    path('error/', views.error, name="error"),
    path('logout/', LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.register, name='register'),

    path('izbornik/student/', views.studentDashboard, name='izbornik_student'),
    path('izbornik/student/enroll_subject/<int:subject_id>/', views.enrollSubject, name='enroll_subject'),
    path('izbornik/student/unenroll_subject/<int:subject_id>/', views.unenrollSubject, name='unenroll_subject'),
    path('izbornik/student/filter_subjects/', views.filterSubjects, name='filter_subjects'),

    path('izbornik/profesor/', views.professorDashboard, name='izbornik_profesor'),
    path('izbornik/profesor/predmeti/', views.professorSubjects, name='predmeti'),
    path('izbornik/profesor/predmeti/studenti/<int:subject_id>/', views.viewStudents, name='view_students'),
    path('izbornik/profesor/predmeti/studenti/izgubljen_potpis/<int:subject_id>/', views.viewStudentsFailed, name='view_students_failed'),
    path('izbornik/profesor/predmeti/studenti/upisani/<int:subject_id>/', views.viewStudentsEnrolled, name='view_students_enrolled'),
    path('izbornik/profesor/predmeti/studenti/polozili/<int:subject_id>/', views.viewStudentsPassed, name='view_students_passed'),

    path('izbornik/admin/', views.AdminDashboard, name='izbornik_admin'),
    path('izbornik/admin/predmeti/', views.subjectAdmin, name='predmeti_lista'),
    path('izbornik/admin/predmeti/update/<int:subject_id>/', views.subjectUpdate, name='subject_update'),
    path('izbornik/admin/predmeti/add/', views.subjectAdd, name='add_subject'),
    path('izbornik/admin/predmeti/studenti/<int:subject_id>/', views.studentsSubject, name='students_subject'),

    path('izbornik/admin/predmeti/upisni_list/<int:student_id>/', views.enrollmentFormAdmin, name='enrollment_form'),
    path('izbornik/admin/predmeti/upisni_list/<int:student_id>/enroll_subject_admin/<int:subject_id>/', views.enrollSubjectAdmin, name='enroll_subject_admin'),
    path('izbornik/admin/predmeti/upisni_list/<int:student_id>/unenroll_subject_admin/<int:subject_id>/', views.unenrollSubjectAdmin, name='unenroll_subject_admin'),

    path('izbornik/admin/studenti/', views.studentAdmin, name='studenti_lista'),
    path('izbornik/admin/studenti/update/<int:student_id>/', views.studentUpdate, name='student_update'),
    path('izbornik/admin/studenti/add/', views.studentAdd, name='add_student'),
    path('izbornik/admin/studenti/upisni_list/<int:student_id>/', views.enrollmentFormAdmin, name='enrollment_form'),

    path('izbornik/admin/profesori/', views.professorAdmin, name='profesori_lista'),
    path('izbornik/admin/profesori/update/<int:professor_id>/', views.professorUpdate, name='professor_update'),
    path('izbornik/admin/profesori/add/', views.professorAdd, name='add_professor'),
    
       # — Usa re_path en vez de path para incluir los módulos con regex internas —
    # 1) URLs para visualizar/usar los formularios
    re_path(r'^forms/', include('fobi.urls.view')),

    # 2) URLs para editar/crear formularios con el form-builder
    re_path(r'^forms/edit/', include('fobi.urls.edit')),

    # si usas el db_store handler:
    re_path(
        r'^forms/plugins/form-handlers/db-store/',
        include('fobi.contrib.plugins.form_handlers.db_store.urls')
    ),
]