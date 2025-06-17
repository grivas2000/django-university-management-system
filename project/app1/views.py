from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages  # <— importar aquí
from .models import *
from .forms import RegisterForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
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
        return redirect('izbornik_student')
    elif request.user.role.role == 'Admin':
        return redirect('izbornik_admin')
    elif request.user.role.role == 'Profesor':
        return redirect('izbornik_profesor')
    else:
        return redirect('error')


def error(request):
    return render(request, 'error.html')


def home(request):
    return HttpResponse("Bienvenido al sistema de gestión universitaria.")

@student_required
def studentDashboard(request):
    student = request.user
    enrolled_subjects = Korisnik_Predmet.objects.filter(korisnik=student)
    unenrolled_subjects = Predmeti.objects.exclude(id__in=enrolled_subjects.values_list('predmeti__id', flat=True))

    semesters = {}

    semesters_count = 8 if student.status.status == 'Izvanredni student' else 6

    for i in range(1, semesters_count + 1):
        semesters[str(i)] = {'enrolled_subjects': [], 'unenrolled_subjects': []}

    for enrollment in enrolled_subjects:
        subject = enrollment.predmeti
        sem_key = str(subject.sem_izv) if student.status.status == 'Izvanredni student' else str(subject.sem_red)
        semesters[sem_key]['enrolled_subjects'].append(subject)

    for subject in unenrolled_subjects:
        sem_key = str(subject.sem_izv) if student.status.status == 'Izvanredni student' else str(subject.sem_red)
        semesters[sem_key]['unenrolled_subjects'].append(subject)

    # Azurira statuse predmeta
    for semester_subjects in semesters.values():
        for subject in semester_subjects['enrolled_subjects']:
            subject.enrollment_status = subject.korisnik_predmet_set.filter(korisnik=student).first().status.status

        for subject in semester_subjects['unenrolled_subjects']:
            subject.enrollment_status = None

    return render(request, 'izbornikStudent.html', {'semesters': semesters, 'student': student})



@student_required
def filterSubjects(request):
    ects = request.GET.get('points')
    semester = request.GET.get('semester')

    enrolled_subjects = Predmeti.objects.filter(korisnik_predmet__status__status='Prijavljen')

    if ects:
        enrolled_subjects = enrolled_subjects.filter(ects__gt=ects) # gt - greater than
    if semester:
        if semester == 'sem_izv':
            enrolled_subjects = enrolled_subjects.filter(sem_izv=semester)
        else:
            enrolled_subjects = enrolled_subjects.filter(sem_red=semester)

    enrolled_subjects = enrolled_subjects.distinct()

    return render(request, 'studentFilterPredmeta.html', {'filter_subjects': enrolled_subjects})


@student_required
def enrollSubject(request, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    student = request.user

    if Korisnik_Predmet.objects.filter(korisnik=student, predmeti=subject).exists():
        return redirect('izbornik_student')

    predmet = Korisnik_Predmet(korisnik=student, predmeti=subject)
    predmet.save()
    return redirect('izbornik_student')


@student_required
def unenrollSubject(request, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    student = request.user

    predmet = Korisnik_Predmet.objects.filter(korisnik=student, predmeti=subject).first()
    if predmet:
        predmet.delete()
    return redirect('izbornik_student')


@professor_required
def professorDashboard(request):
    return render(request, 'izbornikProfesor.html')


@professor_required
def professorSubjects(request):
    professor = request.user
    subjects = Predmeti.objects.filter(nositelj=professor)

    return render(request, 'profesorPredmeti.html', {'subjects': subjects})


@professor_required
def viewStudents(request, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    students = Korisnik_Predmet.objects.filter(predmeti=subject)
    all_status = Status.objects.all()

    if request.method == 'POST':
        for student in students:
            status_id = request.POST.get(f"status_{student.id}")
            status = get_object_or_404(Status, id=status_id)
            student.status = status
            student.save()

        return redirect('view_students', subject_id=subject.id)

    return render(request, 'students.html', {'subject': subject, 'students': students, 'all_status': all_status})


@professor_required
def viewStudentsFailed(request, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    failed_students = Korisnik_Predmet.objects.filter(predmeti=subject, status__status='Izgubljen potpis') # filter condition
    return render(request, 'profesorStudenti1.html', {'subject': subject, 'students': failed_students})


@professor_required
def viewStudentsEnrolled(request, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    enrolled_students = Korisnik_Predmet.objects.filter(predmeti=subject, status__status='Prijavljen')
    return render(request, 'profesorStudenti2.html', {'subject': subject, 'students': enrolled_students})


@professor_required
def viewStudentsPassed(request, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    passed_students = Korisnik_Predmet.objects.filter(predmeti=subject, status__status='Položen')
    return render(request, 'profesorStudenti3.html', {'subject': subject, 'students': passed_students})


@admin_required
def AdminDashboard(request):
    return render(request, 'izbornikAdmin.html')


@admin_required
def subjectAdmin(request):
    subjects = Predmeti.objects.all()

    if request.method == 'POST':
        predmet_id = request.POST.get('predmet_id')
        return redirect('subject_update', predmet_id=predmet_id)

    if request.method == 'GET' and 'add_subject' in request.GET:
        return redirect('add_subject')

    return render(request, 'adminPredmeti.html', {'subjects': subjects})


def subjectUpdate(request, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    # Obtener lista de profesores; aquí según tu lógica: role_id=2 u otro filtro
    professors = Korisnik.objects.filter(role_id=2)

    if request.method == 'POST':
        new_name = request.POST.get('new_name', '').strip()
        new_kod = request.POST.get('new_kod', '').strip()
        new_program = request.POST.get('new_program', '').strip()
        new_ects = request.POST.get('new_ects', '').strip()
        new_sem_red = request.POST.get('new_sem_red', '').strip()
        new_sem_izv = request.POST.get('new_sem_izv', '').strip()
        new_izborni = request.POST.get('new_izborni', '').strip()
        new_nositelj_username = request.POST.get('new_nositelj', '').strip()
        new_horario = request.POST.get('new_horario', '').strip()

        # Validaciones básicas
        if not new_name or not new_kod:
            messages.error(request, "Name y Kod son obligatorios.")
            return render(request, 'updatePredmet.html', {
                'subject': subject,
                'professors': professors
            })

        # Validar valores numéricos (ects, sem_red, sem_izv)
        try:
            ects_val = int(new_ects)
            sem_red_val = int(new_sem_red)
            sem_izv_val = int(new_sem_izv)
        except ValueError:
            messages.error(request, "Ects, semestre regular y semestre extraordinario deben ser números enteros.")
            return render(request, 'updatePredmet.html', {
                'subject': subject,
                'professors': professors
            })

        # Obtener nositelj
        try:
            new_nositelj = Korisnik.objects.get(username=new_nositelj_username)
        except Korisnik.DoesNotExist:
            messages.error(request, "Profesor (nositelj) inválido.")
            return render(request, 'updatePredmet.html', {
                'subject': subject,
                'professors': professors
            })

        # Asignar campos
        subject.name = new_name
        subject.kod = new_kod
        subject.program = new_program
        subject.ects = ects_val
        subject.sem_red = sem_red_val
        subject.sem_izv = sem_izv_val
        subject.izborni = new_izborni
        subject.nositelj = new_nositelj
        subject.horario = new_horario  # asignamos el nuevo campo
        subject.save()

        messages.success(request, "Materia actualizada correctamente.")
        return redirect('predmeti_lista')

    # GET: pasar al template para prellenar
    return render(request, 'updatePredmet.html', {
        'subject': subject,
        'professors': professors
    })


@admin_required
def subjectAdd(request):
    if request.method == 'POST':
        new_name = request.POST.get('new_name', '').strip()
        new_kod = request.POST.get('new_kod', '').strip()
        new_program = request.POST.get('new_program', '').strip()
        new_ects = request.POST.get('new_ects', '').strip()
        new_sem_red = request.POST.get('new_sem_red', '').strip()
        new_sem_izv = request.POST.get('new_sem_izv', '').strip()
        new_izborni = request.POST.get('new_izborni', '').strip()
        new_nositelj_username = request.POST.get('new_nositelj', '').strip()
        new_horario = request.POST.get('new_horario', '').strip()

        # Validaciones básicas
        if not new_name or not new_kod:
            messages.error(request, "Name y Kod son obligatorios.")
            return render(request, 'addPredmet.html', {
                'professors': Korisnik.objects.filter(role_id=2)
            })

        try:
            ects_val = int(new_ects)
            sem_red_val = int(new_sem_red)
            sem_izv_val = int(new_sem_izv)
        except ValueError:
            messages.error(request, "Ects, semestre regular y semestre extraordinario deben ser números enteros.")
            return render(request, 'addPredmet.html', {
                'professors': Korisnik.objects.filter(role_id=2)
            })

        try:
            new_nositelj = Korisnik.objects.get(username=new_nositelj_username)
        except Korisnik.DoesNotExist:
            messages.error(request, "Profesor (nositelj) inválido.")
            return render(request, 'addPredmet.html', {
                'professors': Korisnik.objects.filter(role_id=2)
            })

        predmet = Predmeti(
            name=new_name,
            kod=new_kod,
            program=new_program,
            ects=ects_val,
            sem_red=sem_red_val,
            sem_izv=sem_izv_val,
            izborni=new_izborni,
            nositelj=new_nositelj,
            horario=new_horario  # asignamos aquí también
        )
        predmet.save()
        messages.success(request, "Materia creada correctamente.")
        return redirect('predmeti_lista')

    # GET
    professors = Korisnik.objects.filter(role_id=2)
    return render(request, 'addPredmet.html', {'professors': professors})

@admin_required
def studentAdmin(request):
    students = Korisnik.objects.filter(role_id=3)
    return render(request, 'adminStudenti.html', {'students': students})


@admin_required
def studentUpdate(request, student_id):
    student = get_object_or_404(Korisnik, id=student_id)

    if request.method == 'POST':
        # guardar valores originales para comparar
        orig_first = student.first_name or ''
        orig_last = student.last_name or ''
        orig_user = student.username or ''
        orig_email = student.email or ''

        # obtener datos del formulario
        new_first_name = request.POST.get('new_first_name', '').strip()
        new_last_name = request.POST.get('new_last_name', '').strip()
        new_username = request.POST.get('new_username', '').strip()
        new_email = request.POST.get('new_email', '').strip()
        new_password = request.POST.get('new_password', '')

        # Validaciones básicas
        if not new_first_name or not new_last_name or not new_username:
            messages.error(request, "Name, surname and username are required.")
            return render(request, 'updateStudent.html', {'student': student})

        # Unicidad username/email
        if Korisnik.objects.exclude(id=student.id).filter(username=new_username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'updateStudent.html', {'student': student})
        if new_email and Korisnik.objects.exclude(id=student.id).filter(email=new_email).exists():
            messages.error(request, "Email already in use.")
            return render(request, 'updateStudent.html', {'student': student})

        # Determinar si hay cambios
        changed = False
        if new_first_name != orig_first:
            student.first_name = new_first_name
            changed = True
        if new_last_name != orig_last:
            student.last_name = new_last_name
            changed = True
        if new_username != orig_user:
            student.username = new_username
            changed = True
        if new_email != orig_email:
            student.email = new_email
            changed = True
        if new_password:
            student.set_password(new_password)
            changed = True

        if changed:
            student.save()
            messages.success(request, "Student updated successfully.")
            # Redirigir al inicio del dashboard; usa el nombre de URL correcto
            return redirect('izbornik_admin')
        else:
            messages.info(request, "No changes detected.")
            # quedarse en la misma página para que el usuario vea mensaje
            return render(request, 'updateStudent.html', {'student': student})

    # GET
    return render(request, 'updateStudent.html', {'student': student})

@admin_required
def studentAdd(request):
    status_list = StatusStudenta.objects.all()

    if request.method == 'POST':
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_username = request.POST.get('new_username')
        new_email = request.POST.get('new_email')
        new_password = request.POST.get('new_password')
        new_status_id = request.POST.get('new_status_id')

        new_status = get_object_or_404(StatusStudenta, id=new_status_id)

        student = Korisnik(
            first_name=new_first_name,
            last_name=new_last_name,
            username=new_username,
            email=new_email,
            password=make_password(new_password),
            role_id=3,
            status=new_status
        )
        student.save()
        return redirect('studenti_lista')

    return render(request, 'addStudent.html', {'status_list': status_list})


@admin_required
def professorAdmin(request):
    professors = Korisnik.objects.filter(role_id=2)
    context = {'professors': professors}
    return render(request, 'adminProfesori.html', context)


@admin_required
def professorUpdate(request, professor_id):
    professor = get_object_or_404(Korisnik, id=professor_id)

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

        return redirect('profesori_lista')

    return render(request, 'updateProfesor.html', {'professor': professor})


@admin_required
def professorAdd(request):
    if request.method == 'POST':
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        new_username = request.POST.get('new_username')
        new_email = request.POST.get('new_email')
        new_password = request.POST.get('new_password')

        profesor = Korisnik(
            first_name=new_first_name,
            last_name=new_last_name,
            username=new_username,
            email=new_email,
            password=make_password(new_password),
            role_id=2
        )
        profesor.save()
        return redirect('profesori_lista')

    professors = Korisnik.objects.filter(role_id=2)

    return render(request, 'addProfesor.html', {'professors': professors})


@admin_required
def studentsSubject(request, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    students = Korisnik_Predmet.objects.filter(predmeti=subject)

    return render(request, 'adminStudentiPredmet.html', {'subject': subject, 'students': students})


@admin_required
def enrollmentFormAdmin(request, student_id):
    student = get_object_or_404(Korisnik, id=student_id)
    enrolled_subjects = Korisnik_Predmet.objects.filter(korisnik=student)
    unenrolled_subjects = Predmeti.objects.exclude(id__in=enrolled_subjects.values_list('predmeti__id', flat=True)) # dohvacanje id-a od povezanog modela i referenciranje polja

    semesters = {}

    sem_count = 8 if student.status.status == 'Izvanredni student' else 6

    for i in range(1, sem_count + 1):
        semesters[str(i)] = {'enrolled_subjects': [], 'unenrolled_subjects': []}

    for enrollment in enrolled_subjects:
        subject = enrollment.predmeti
        sem_key = str(subject.sem_izv) if student.status.status == 'Izvanredni student' else str(subject.sem_red)
        semesters[sem_key]['enrolled_subjects'].append(subject)

    for subject in unenrolled_subjects:
        sem_key = str(subject.sem_izv) if student.status.status == 'Izvanredni student' else str(subject.sem_red)
        semesters[sem_key]['unenrolled_subjects'].append(subject)

    for semester_subjects in semesters.values():
        for subject in semester_subjects['enrolled_subjects']:
            enrollment = Korisnik_Predmet.objects.get(korisnik=student, predmeti=subject)
            subject.enrollment_status = enrollment.status.status

        for subject in semester_subjects['unenrolled_subjects']:
            subject.enrollment_status = None

    return render(request, 'adminUpisniList.html', {'semesters': semesters, 'student': student})



@admin_required
def enrollSubjectAdmin(request, student_id, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    student = get_object_or_404(Korisnik, id=student_id)

    if Korisnik_Predmet.objects.filter(korisnik=student, predmeti=subject).exists():
        return redirect('enrollment_form', student_id=student_id)

    predmet = Korisnik_Predmet(korisnik=student, predmeti=subject)
    predmet.save()

    return redirect('enrollment_form', student_id=student_id)


@admin_required
def unenrollSubjectAdmin(request, student_id, subject_id):
    subject = get_object_or_404(Predmeti, id=subject_id)
    student = get_object_or_404(Korisnik, id=student_id)

    predmet = Korisnik_Predmet.objects.filter(korisnik=student, predmeti=subject).first()
    if predmet:
        predmet.delete()

    return redirect('enrollment_form', student_id=student_id)

