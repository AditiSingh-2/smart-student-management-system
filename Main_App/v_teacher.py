from datetime import date
from random import randint
from django.contrib import messages
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings

from Main_App.models import MyUser, Notes, Notification, Student, Result, Teacher, Course, Attendance, InternalMarks, ExamSchedule, Timetable
from Main_App.restrictions import is_authenticated, is_teacher

@is_authenticated
@is_teacher
def t_home(request):
    try:
        teacher = Teacher.objects.get(admin=request.user.id)
        # Get courses taught by this teacher
        courses = Course.objects.filter(teacher=teacher)
        
        # Count students per department
        cs_count = Student.objects.filter(department='CS').count()
        it_count = Student.objects.filter(department='IT').count()
        entc_count = Student.objects.filter(department='ENTC').count()
        mech_count = Student.objects.filter(department='MECH').count()
        civil_count = Student.objects.filter(department='CIVIL').count()

        male_count = Student.objects.filter(gender="Male").count()
        female_count = Student.objects.filter(gender="Female").count()
        other_count = Student.objects.filter(gender="Other").count()

        context = {
            "teacher": teacher,
            "courses": courses,
            "cs_count": cs_count,
            "it_count": it_count,
            "entc_count": entc_count,
            "mech_count": mech_count,
            "civil_count": civil_count,
            "male_count": male_count,
            "female_count": female_count,
            "other_count": other_count,
        }
        return render(request, 'teacher/t_home.html', context)
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_teacher
def t_profile(request):
    try:
        teacher = Teacher.objects.get(admin=request.user.id)
        return render(request, 'teacher/t_profile.html', {'teacher': teacher})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_teacher
def t_saveprofile(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    teacher_id = request.POST.get('teacher_id')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    email = request.POST.get('email')
    address = request.POST.get('address')
    gender = request.POST.get('gender')
    password = request.POST.get('password')
    try:
        user = MyUser.objects.get(id=teacher_id)
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        if password is not None and password != "":
            user.set_password(password)
        user.save()
        teacher = Teacher.objects.get(admin=teacher_id)
        teacher.address = address
        teacher.gender = gender
        teacher.save()
        messages.success(request, "Profile updated successfully")
        return HttpResponseRedirect('/teacherprofile/')
    except Exception as e:
        messages.error(request, f"Failed to update profile: {e}")
        return HttpResponseRedirect('/teacherprofile/')

@is_authenticated
@is_teacher
def t_addstudent(request):
    genders = Student.GENDER_CHOICES
    years = Student.YEAR_CHOICES
    departments = Student.DEPARTMENT_CHOICES
    return render(request, 'teacher/t_addstudent.html', {
        'genders': genders,
        'years': years,
        'departments': departments
    })

@is_authenticated
@is_teacher
def t_savestudent(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    email = request.POST.get('email')
    address = request.POST.get('address')
    gender = request.POST.get('gender')
    year = request.POST.get('year')
    department = request.POST.get('department')
    roll_number = request.POST.get('roll_number')
    phone = request.POST.get('phone')
    section = request.POST.get('section')
    password = "Student@100"

    def random_username():
        r = randint(1000, 9999)
        username = "SC" + str(date.today().year) + str(r)
        if MyUser.objects.filter(username=username).exists():
            return random_username()
        return username

    try:
        username = random_username()
        user = MyUser.objects.create_user(
            username=username, password=password,
            email=email, first_name=firstname,
            last_name=lastname, user_type=3
        )
        user.student.address = address
        user.student.gender = gender
        user.student.year = year
        user.student.department = department
        user.student.roll_number = roll_number
        user.student.phone = phone
        user.student.section = section
        user.student.college_email = email
        user.save()
        messages.success(request, "Student added successfully")
        return HttpResponseRedirect("/t_addstudent/")
    except Exception as e:
        messages.error(request, f"Failed to add student: {e}")
        return HttpResponseRedirect("/t_addstudent/")

@is_authenticated
@is_teacher
def t_viewstudent(request):
    try:
        teacher = Teacher.objects.get(admin=request.user.id)
        # Show students in teacher's courses departments
        courses = Course.objects.filter(teacher=teacher)
        departments = courses.values_list('department', flat=True).distinct()
        students = Student.objects.filter(department__in=departments)
        return render(request, 'teacher/t_viewstudent.html', {'students': students})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_teacher
def t_resetspass(request, student_id):
    try:
        user = MyUser.objects.get(id=student_id)
        user.set_password("Student@100")
        user.save()
        messages.success(request, "Password reset successfully to Student@100")
    except Exception as e:
        messages.error(request, f"Failed to reset password: {e}")
    return HttpResponseRedirect("/t_viewstudent/")

@is_authenticated
@is_teacher
def t_addnotification(request):
    return render(request, 'teacher/t_addnotification.html')

@is_authenticated
@is_teacher
def t_savenotification(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    try:
        heading = request.POST.get('heading')
        message = request.POST.get('message')
        created_by = request.user.username
        notification = Notification.objects.create(
            heading=heading, message=message, created_by=created_by
        )
        notification.save()
        messages.success(request, "Notification added successfully")
        return HttpResponseRedirect("/t_addnotification/")
    except Exception as e:
        messages.error(request, f"Failed to add Notification: {e}")
        return HttpResponseRedirect("/t_addnotification/")

@is_authenticated
@is_teacher
def t_deletenotification(request):
    try:
        notifications = Notification.objects.filter(created_by=request.user.username)
        return render(request, 'teacher/t_deletenotification.html', {'notifications': notifications})
    except:
        return render(request, 'teacher/t_deletenotification.html')

@is_authenticated
@is_teacher
def t_removenotification(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        messages.success(request, "Notification deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete Notification: {e}")
    return HttpResponseRedirect("/t_deletenotification/")

@is_authenticated
@is_teacher
def t_viewnotification(request):
    try:
        notifications = Notification.objects.all()
        return render(request, 'teacher/t_viewnotification.html', {'notifications': notifications})
    except:
        return render(request, 'teacher/t_viewnotification.html')

@is_authenticated
@is_teacher
def t_addresult(request):
    try:
        teacher = Teacher.objects.get(admin=request.user.id)
        courses = Course.objects.filter(teacher=teacher)
        return render(request, 'teacher/t_addresult.html', {'courses': courses})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_teacher
def t_saveresult(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    try:
        title = request.POST.get('title')
        course_id = request.POST.get('course')
        resultfile = request.FILES['resultfile']
        created_by = request.user.username
        course = Course.objects.get(id=course_id)
        result = Result.objects.create(
            title=title, file=resultfile,
            course=course, created_by=created_by
        )
        result.save()
        messages.success(request, "Result uploaded successfully")
        return HttpResponseRedirect("/t_addresult/")
    except Exception as e:
        messages.error(request, f"Failed to upload result: {e}")
        return HttpResponseRedirect("/t_addresult/")

@is_authenticated
@is_teacher
def t_deleteresult(request):
    try:
        results = Result.objects.filter(created_by=request.user.username)
        return render(request, 'teacher/t_deleteresult.html', {'results': results})
    except:
        return render(request, 'teacher/t_deleteresult.html')

@is_authenticated
@is_teacher
def t_removeresult(request, result_id):
    try:
        result = Result.objects.get(id=result_id)
        result.file.delete()
        result.delete()
        messages.success(request, "Result deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete result: {e}")
    return HttpResponseRedirect("/t_deleteresult/")

@is_authenticated
@is_teacher
def t_viewresult(request):
    results = Result.objects.all()
    return render(request, 'teacher/t_viewresult.html', {'results': results})

@is_authenticated
@is_teacher
def t_addnotes(request):
    try:
        teacher = Teacher.objects.get(admin=request.user.id)
        courses = Course.objects.filter(teacher=teacher)
        return render(request, 'teacher/t_addnotes.html', {'courses': courses})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_teacher
def t_savenotes(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    try:
        title = request.POST.get('title')
        course_id = request.POST.get('course')
        file = request.FILES['notes']
        created_by = request.user.username
        course = Course.objects.get(id=course_id)
        notes = Notes.objects.create(
            title=title, file=file,
            course=course, created_by=created_by
        )
        notes.save()
        messages.success(request, "Notes uploaded successfully")
        return HttpResponseRedirect("/t_addnotes/")
    except Exception as e:
        messages.error(request, f"Failed to upload notes: {e}")
        return HttpResponseRedirect("/t_addnotes/")

@is_authenticated
@is_teacher
def t_deletenotes(request):
    try:
        notes = Notes.objects.filter(created_by=request.user.username)
        return render(request, 'teacher/t_deletenotes.html', {'notes': notes})
    except:
        return render(request, 'teacher/t_deletenotes.html')

@is_authenticated
@is_teacher
def t_removenotes(request, notes_id):
    try:
        notes = Notes.objects.get(id=notes_id)
        notes.file.delete()
        notes.delete()
        messages.success(request, "Note deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete note: {e}")
    return HttpResponseRedirect("/t_deletenotes/")

@is_authenticated
@is_teacher
def t_viewnotes(request):
    notes = Notes.objects.all()
    return render(request, 'teacher/t_viewnotes.html', {'notes': notes})

@is_authenticated
@is_teacher
def t_addattendance(request):
    try:
        teacher = Teacher.objects.get(admin=request.user.id)
        courses = Course.objects.filter(teacher=teacher)
        return render(request, 'teacher/t_addattendance.html', {'courses': courses})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_teacher
def t_saveattendance(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    try:
        course_id = request.POST.get('course')
        date_val = request.POST.get('date')
        course = Course.objects.get(id=course_id)
        students = Student.objects.filter(
            department=course.department,
            year=course.year
        )
        for student in students:
            status = request.POST.get(f'attendance_{student.id}')
            is_present = status == 'present'
            Attendance.objects.update_or_create(
                student=student,
                course=course,
                date=date_val,
                defaults={'is_present': is_present}
            )
        messages.success(request, "Attendance saved successfully")
        return HttpResponseRedirect("/t_addattendance/")
    except Exception as e:
        messages.error(request, f"Failed to save attendance: {e}")
        return HttpResponseRedirect("/t_addattendance/")

@is_authenticated
@is_teacher
def t_addmarks(request):
    try:
        teacher = Teacher.objects.get(admin=request.user.id)
        courses = Course.objects.filter(teacher=teacher)
        return render(request, 'teacher/t_addmarks.html', {'courses': courses})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_teacher
def t_savemarks(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    try:
        course_id = request.POST.get('course')
        exam_type = request.POST.get('exam_type')
        max_marks = request.POST.get('max_marks')
        course = Course.objects.get(id=course_id)
        students = Student.objects.filter(
            department=course.department,
            year=course.year
        )
        for student in students:
            marks_obtained = request.POST.get(f'marks_{student.id}')
            if marks_obtained:
                InternalMarks.objects.update_or_create(
                    student=student,
                    course=course,
                    exam_type=exam_type,
                    defaults={
                        'marks_obtained': marks_obtained,
                        'max_marks': max_marks
                    }
                )
        messages.success(request, "Marks saved successfully")
        return HttpResponseRedirect("/t_addmarks/")
    except Exception as e:
        messages.error(request, f"Failed to save marks: {e}")
        return HttpResponseRedirect("/t_addmarks/")
