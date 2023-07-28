from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import RegisterForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from .decorators import *


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('myProfile') 
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

  
def myProfile(request):
    if request.user.role.role == 'Student':
        return redirect('menu_student')
    elif request.user.role.role == 'Admin':
        return redirect('menu_admin')
    elif request.user.role.role == 'Professor':
        return redirect('menu_professor')
    else:
        return redirect('error')


def error(request):
    return render(request, 'error.html')


@student_required
def studentDashboard(request):
    student = request.user
    enrolled_subjects = User_Subjects.objects.filter(user=student)
    unenrolled_subjects = Subjects.objects.exclude(id__in=enrolled_subjects.values_list('subjects__id', flat=True))

    semesters = {}

    semesters_count = 8 if student.status.status == 'Irregular student' else 6

    for i in range(1, semesters_count + 1):
        semesters[str(i)] = {'enrolled_subjects': [], 'unenrolled_subjects': []}

    for enrollment in enrolled_subjects:
        subject = enrollment.subjects
        sem_key = str(subject.sem_irr) if student.status.status == 'Irregular student' else str(subject.sem_reg)
        semesters[sem_key]['enrolled_subjects'].append(subject)

    for subject in unenrolled_subjects:
        sem_key = str(subject.sem_irr) if student.status.status == 'Irregular student' else str(subject.sem_reg)
        semesters[sem_key]['unenrolled_subjects'].append(subject)


    for semester_subjects in semesters.values():
        for subject in semester_subjects['enrolled_subjects']:
            subject.enrollment_status = subject.user_subjects_set.filter(user=student).first().status.status

        for subject in semester_subjects['unenrolled_subjects']:
            subject.enrollment_status = None

    return render(request, 'menuStudent.html', {'semesters': semesters, 'student': student})


@student_required
def filterSubjects(request):
    ects = request.GET.get('points')
    semester = request.GET.get('semester')

    enrolled_subjects = Subjects.objects.filter(user_subjects__status__status='Enrolled')

    if ects:
        enrolled_subjects = enrolled_subjects.filter(ects__gt=ects) # gt - greater than
    if semester:
        if semester == 'sem_irr':
            enrolled_subjects = enrolled_subjects.filter(sem_irr=semester)
        else:
            enrolled_subjects = enrolled_subjects.filter(sem_reg=semester)

    enrolled_subjects = enrolled_subjects.distinct()

    return render(request, 'studentFilterSubjects.html', {'filter_subjects': enrolled_subjects})


@student_required
def enrollSubject(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    student = request.user

    if User_Subjects.objects.filter(user=student, subjects=subject).exists():
        return redirect('menu_student')

    subjects = User_Subjects(user=student, subjects=subject)
    subjects.save()
    return redirect('menu_student')


@student_required
def unenrollSubject(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    student = request.user

    subject = User_Subjects.objects.filter(user=student, subjects=subject).first()
    if subject:
        subject.delete()
    return redirect('menu_student')


@professor_required
def professorDashboard(request):
    return render(request, 'menuProfessor.html')


@professor_required
def professorSubjects(request):
    professor = request.user
    subjects = Subjects.objects.filter(professor=professor)

    return render(request, 'professorSubjects.html', {'subjects': subjects})


@professor_required
def viewStudents(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    students = User_Subjects.objects.filter(subjects=subject)
    all_status = SubjectStatus.objects.all()

    if request.method == 'POST':
        for student in students:
            status_id = request.POST.get(f"status_{student.id}")
            status = get_object_or_404(SubjectStatus, id=status_id)
            student.status = status
            student.save()

        return redirect('view_students', subject_id=subject.id)

    return render(request, 'professorAllStudents.html', {'subject': subject, 'students': students, 'all_status': all_status})


@professor_required
def viewStudentsFailed(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    failed_students = User_Subjects.objects.filter(subjects=subject, status__status='Failed')
    return render(request, 'professorFailedStudents.html', {'subject': subject, 'students': failed_students})


@professor_required
def viewStudentsEnrolled(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    enrolled_students = User_Subjects.objects.filter(subjects=subject, status__status='Enrolled')
    return render(request, 'professorEnrolledStudents.html', {'subject': subject, 'students': enrolled_students})


@professor_required
def viewStudentsPassed(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    passed_students = User_Subjects.objects.filter(subjects=subject, status__status='Passed')
    return render(request, 'professorPassedStudents.html', {'subject': subject, 'students': passed_students})


@admin_required
def AdminDashboard(request):
    return render(request, 'menuAdmin.html')


@admin_required
def subjectAdmin(request):
    subjects = Subjects.objects.all()

    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        return redirect('subject_update', subject_id=subject_id)

    if request.method == 'GET' and 'add_subject' in request.GET:
        return redirect('add_subject')

    return render(request, 'adminSubjects.html', {'subjects': subjects})


@admin_required
def subjectUpdate(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    professors = User.objects.filter(role_id=2)

    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        new_code = request.POST.get('new_code')
        new_program = request.POST.get('new_program')
        new_ects = request.POST.get('new_ects')
        new_sem_reg= request.POST.get('new_sem_reg')
        new_sem_irr = request.POST.get('new_sem_irr')
        new_elective = request.POST.get('new_elective')

        new_professor_username = request.POST.get('new_professor')
        new_professor = get_object_or_404(User, username=new_professor_username)

        subject.name = new_name
        subject.code = new_code
        subject.program = new_program
        subject.ects = new_ects
        subject.sem_reg = new_sem_reg
        subject.sem_irr = new_sem_irr
        subject.elective = new_elective
        subject.professor = new_professor
        subject.save()

        return redirect('subjects_list')
    
    return render(request, 'adminUpdateSubject.html', {'subject': subject, 'subject_id': subject_id, 'professors': professors})


@admin_required
def subjectAdd(request):
    if request.method == 'POST':
        new_name = request.POST.get('new_name')
        new_code = request.POST.get('new_code')
        new_program = request.POST.get('new_program')
        new_ects = request.POST.get('new_ects')
        new_sem_reg= request.POST.get('new_sem_reg')
        new_sem_irr = request.POST.get('new_sem_irr')
        new_elective = request.POST.get('new_elective')
        new_professor_username = request.POST.get('new_professor')

        new_professor = User.objects.get(username=new_professor_username)

        subject = Subjects(
            name=new_name,
            code=new_code,
            program=new_program,
            ects=new_ects,
            sem_reg=new_sem_reg,
            sem_irr=new_sem_irr,
            elective=new_elective,
            professor=new_professor
        )
        subject.save()
        return redirect('subjects_list')

    professor = User.objects.filter(role_id=2)

    return render(request, 'adminAddSubject.html', {'professors': professor})


@admin_required
def studentAdmin(request):
    students = User.objects.filter(role_id=3)
    return render(request, 'adminStudents.html', {'students': students})


@admin_required
def studentUpdate(request, student_id):
    student = get_object_or_404(User, id=student_id)
    status_list = StudentStatus.objects.all()

    if request.method == 'POST':
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_username = request.POST.get('new_username')
        new_email = request.POST.get('new_email')
        new_password = request.POST.get('new_password')
        new_status_id = request.POST.get('new_status')

        new_status = get_object_or_404(StudentStatus, id=new_status_id)

        student.first_name = new_first_name
        student.last_name = new_last_name
        student.username = new_username
        student.email = new_email
        student.password = make_password(new_password)
        student.status = new_status
        student.save()

        return redirect('students_list')

    return render(request, 'adminUpdateStudent.html', {'student': student, 'student_id': student_id, 'status_list': status_list})


@admin_required
def studentAdd(request):
    status_list = StudentStatus.objects.all()

    if request.method == 'POST':
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_username = request.POST.get('new_username')
        new_email = request.POST.get('new_email')
        new_password = request.POST.get('new_password')
        new_status_id = request.POST.get('new_status_id')

        new_status = get_object_or_404(StudentStatus, id=new_status_id)

        student = User(
            first_name=new_first_name,
            last_name=new_last_name,
            username=new_username,
            email=new_email,
            password=make_password(new_password),
            role_id=3,
            status=new_status
        )
        student.save()
        return redirect('students_list')

    return render(request, 'adminAddStudent.html', {'status_list': status_list})


@admin_required
def professorAdmin(request):
    professors = User.objects.filter(role_id=2)
    context = {'professors': professors}
    return render(request, 'adminProfessors.html', context)


@admin_required
def professorUpdate(request, professor_id):
    professor = get_object_or_404(User, id=professor_id)

    if request.method == 'POST':
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_username = request.POST.get('new_username')
        new_email = request.POST.get('new_email')
        new_password = request.POST.get('new_password')

        professor.first_name = new_first_name
        professor.last_name = new_last_name
        professor.username = new_username
        professor.email = new_email
        professor.password = make_password(new_password)
        professor.save()

        return redirect('professors_list')

    return render(request, 'adminUpdateProfesor.html', {'professor': professor})


@admin_required
def professorAdd(request):
    if request.method == 'POST':
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_username = request.POST.get('new_username')
        new_email = request.POST.get('new_email')
        new_password = request.POST.get('new_password')

        professor = User(
            first_name=new_first_name,
            last_name=new_last_name,
            username=new_username,
            email=new_email,
            password=make_password(new_password),
            role_id=2
        )
        professor.save()
        return redirect('professors_list')

    professors = User.objects.filter(role_id=2)

    return render(request, 'adminAddProfesor.html', {'professors': professors})


@admin_required
def studentsSubject(request, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    students = User_Subjects.objects.filter(subjects=subject)

    return render(request, 'adminStudentList.html', {'subject': subject, 'students': students})


@admin_required
def enrollmentFormAdmin(request, student_id):
    student = get_object_or_404(User, id=student_id)
    enrolled_subjects = User_Subjects.objects.filter(user=student)
    unenrolled_subjects = Subjects.objects.exclude(id__in=enrolled_subjects.values_list('subjects__id', flat=True))

    semesters = {}

    sem_count = 8 if student.status.status == 'Irregular student' else 6

    for i in range(1, sem_count + 1):
        semesters[str(i)] = {'enrolled_subjects': [], 'unenrolled_subjects': []}

    for enrollment in enrolled_subjects:
        subject = enrollment.subjects
        sem_key = str(subject.sem_irr) if student.status.status == 'Irregular student' else str(subject.sem_reg)
        semesters[sem_key]['enrolled_subjects'].append(subject)

    for subject in unenrolled_subjects:
        sem_key = str(subject.sem_irr) if student.status.status == 'Irregular student' else str(subject.sem_reg)
        semesters[sem_key]['unenrolled_subjects'].append(subject)

    for semester_subjects in semesters.values():
        for subject in semester_subjects['enrolled_subjects']:
            enrollment = User_Subjects.objects.get(user=student, subjects=subject)
            subject.enrollment_status = enrollment.status.status

        for subject in semester_subjects['unenrolled_subjects']:
            subject.enrollment_status = None

    return render(request, 'adminStudentEnrollmentForm.html', {'semesters': semesters, 'student': student})



@admin_required
def enrollSubjectAdmin(request, student_id, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    student = get_object_or_404(User, id=student_id)

    if User_Subjects.objects.filter(user=student, subjects=subject).exists():
        return redirect('enrollment_form', student_id=student_id)

    subject = User_Subjects(user=student, subjects=subject)
    subject.save()

    return redirect('enrollment_form', student_id=student_id)


@admin_required
def unenrollSubjectAdmin(request, student_id, subject_id):
    subject = get_object_or_404(Subjects, id=subject_id)
    student = get_object_or_404(User, id=student_id)

    subject = User_Subjects.objects.filter(user=student, subjects=subject).first()
    if subject:
        subject.delete()

    return redirect('enrollment_form', student_id=student_id)