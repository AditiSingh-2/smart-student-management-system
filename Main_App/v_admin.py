import os
import joblib
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib import admin
from random import randint
from datetime import date
from django.conf import settings
from Main_App.models import MyUser, Notes, Notification, Result, Teacher, Student, Course, ExamSchedule, FeeStatus, Attendance, InternalMarks

from Main_App.restrictions import is_admin, is_authenticated

# Load ML model safely
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "student_model.pkl")

try:
    model = joblib.load(model_path)
except Exception as e:
    model = None
    print(f"ML model not loaded: {e}")

@is_authenticated
@is_admin
def a_home(request):
    cs_count = Student.objects.filter(department='CS').count()
    it_count = Student.objects.filter(department='IT').count()
    entc_count = Student.objects.filter(department='ENTC').count()
    mech_count = Student.objects.filter(department='MECH').count()
    civil_count = Student.objects.filter(department='CIVIL').count()

    male_count = Student.objects.filter(gender="Male").count()
    female_count = Student.objects.filter(gender="Female").count()
    other_count = Student.objects.filter(gender="Other").count()

    year1_count = Student.objects.filter(year=1).count()
    year2_count = Student.objects.filter(year=2).count()
    year3_count = Student.objects.filter(year=3).count()
    year4_count = Student.objects.filter(year=4).count()

    context = {
        "cs_count": cs_count,
        "it_count": it_count,
        "entc_count": entc_count,
        "mech_count": mech_count,
        "civil_count": civil_count,
        "male_count": male_count,
        "female_count": female_count,
        "other_count": other_count,
        "year1_count": year1_count,
        "year2_count": year2_count,
        "year3_count": year3_count,
        "year4_count": year4_count,
    }
    return render(request, 'admin/a_home.html', context)

@is_authenticated
@is_admin
def adminprofile(request):
    return render(request, 'admin/a_profile.html')

@is_authenticated
@is_admin
def addteacher(request):
    genders = Teacher.GENDER_CHOICES
    return render(request, 'admin/a_addteacher.html', {'genders': genders})

@is_authenticated
@is_admin
def saveteacher(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    email = request.POST.get('email')
    address = request.POST.get('address')
    gender = request.POST.get('gender')
    password = "Teacher@100"

    def random_username():
        r = randint(1000, 9999)
        username = "TC" + str(date.today().year) + str(r)
        if MyUser.objects.filter(username=username).exists():
            return random_username()
        return username

    try:
        username = random_username()
        user = MyUser.objects.create_user(
            username=username, password=password,
            email=email, first_name=firstname,
            last_name=lastname, user_type=2
        )
        user.teacher.address = address
        user.teacher.gender = gender
        user.save()
        messages.success(request, "Teacher added successfully")
        return HttpResponseRedirect("/addteacher/")
    except Exception as e:
        messages.error(request, f"Failed to add teacher: {e}")
        return HttpResponseRedirect("/addteacher/")

@is_authenticated
@is_admin
def manageteacher(request):
    teachers = Teacher.objects.all()
    return render(request, 'admin/a_manageteacher.html', {'teachers': teachers})

@is_authenticated
@is_admin
def deleteteacher(request, teacher_id):
    try:
        customuser = MyUser.objects.get(id=teacher_id)
        customuser.delete()
        messages.success(request, "Teacher deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete Teacher: {e}")
    return HttpResponseRedirect("/manageteacher/")

@is_authenticated
@is_admin
def resetteacherpass(request, teacher_id):
    try:
        password = "Teacher@100"
        user = MyUser.objects.get(id=teacher_id)
        user.set_password(password)
        user.save()
        messages.success(request, "Password reset successfully to Teacher@100")
    except Exception as e:
        messages.error(request, f"Failed to reset password: {e}")
    return HttpResponseRedirect("/manageteacher/")

@is_authenticated
@is_admin
def editteacher(request, teacher_id):
    teacher = Teacher.objects.get(admin=teacher_id)
    return render(request, 'admin/a_editteacher.html', {'teacher': teacher})

@is_authenticated
@is_admin
def saveeditteacher(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    teacher_id = request.POST.get('teacher_id')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    email = request.POST.get('email')
    address = request.POST.get('address')
    gender = request.POST.get('gender')
    try:
        user = MyUser.objects.get(id=teacher_id)
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        user.save()
        teacher = Teacher.objects.get(admin=teacher_id)
        teacher.address = address
        teacher.gender = gender
        teacher.save()
        messages.success(request, "Teacher updated successfully")
        return HttpResponseRedirect("/editteacher/" + teacher_id)
    except Exception as e:
        messages.error(request, f"Failed to update teacher: {e}")
        return HttpResponseRedirect("/editteacher/" + teacher_id)

@is_authenticated
@is_admin
def addstudent(request):
    genders = Student.GENDER_CHOICES
    years = Student.YEAR_CHOICES
    departments = Student.DEPARTMENT_CHOICES
    return render(request, 'admin/a_addstudent.html', {
        'genders': genders,
        'years': years,
        'departments': departments
    })

@is_authenticated
@is_admin
def savestudent(request):
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
        return HttpResponseRedirect("/addstudent/")
    except Exception as e:
        messages.error(request, f"Failed to add student: {e}")
        return HttpResponseRedirect("/addstudent/")

@is_authenticated
@is_admin
def managestudent(request):
    students = Student.objects.all()
    return render(request, 'admin/a_managestudent.html', {'students': students})

@is_authenticated
@is_admin
def deletestudent(request, student_id):
    try:
        customuser = MyUser.objects.get(id=student_id)
        customuser.delete()
        messages.success(request, "Student deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete Student: {e}")
    return HttpResponseRedirect("/managestudent/")

@is_authenticated
@is_admin
def resetstudentpass(request, student_id):
    try:
        password = "Student@100"
        user = MyUser.objects.get(id=student_id)
        user.set_password(password)
        user.save()
        messages.success(request, "Password reset successfully to Student@100")
    except Exception as e:
        messages.error(request, f"Failed to reset password: {e}")
    return HttpResponseRedirect("/managestudent/")

@is_authenticated
@is_admin
def editstudent(request, student_id):
    student = Student.objects.get(admin=student_id)
    departments = Student.DEPARTMENT_CHOICES
    years = Student.YEAR_CHOICES
    return render(request, 'admin/a_editstudent.html', {
        'student': student,
        'departments': departments,
        'years': years
    })

@is_authenticated
@is_admin
def saveeditstudent(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    student_id = request.POST.get('student_id')
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
    try:
        user = MyUser.objects.get(id=student_id)
        user.email = email
        user.first_name = firstname
        user.last_name = lastname
        user.save()
        student = Student.objects.get(admin=student_id)
        student.address = address
        student.gender = gender
        student.year = year
        student.department = department
        student.roll_number = roll_number
        student.phone = phone
        student.section = section
        student.save()
        messages.success(request, "Student updated successfully")
        return HttpResponseRedirect("/editstudent/" + student_id)
    except Exception as e:
        messages.error(request, f"Failed to update student: {e}")
        return HttpResponseRedirect("/editstudent/" + student_id)

@is_authenticated
@is_admin
def a_addnotification(request):
    return render(request, 'admin/a_addnotification.html')

@is_authenticated
@is_admin
def a_savenotification(request):
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
        return HttpResponseRedirect("/a_addnotification/")
    except Exception as e:
        messages.error(request, f"Failed to add Notification: {e}")
        return HttpResponseRedirect("/a_addnotification/")

@is_authenticated
@is_admin
def managenotification(request):
    notifications = Notification.objects.all()
    return render(request, 'admin/a_managenotification.html', {'notifications': notifications})

@is_authenticated
@is_admin
def a_deletenotification(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        messages.success(request, "Notification deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete Notification: {e}")
    return HttpResponseRedirect("/managenotification/")

@is_authenticated
@is_admin
def a_addresult(request):
    courses = Course.objects.all()
    return render(request, 'admin/a_addresult.html', {'courses': courses})

@is_authenticated
@is_admin
def a_saveresult(request):
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
        return HttpResponseRedirect("/a_addresult/")
    except Exception as e:
        messages.error(request, f"Failed to upload result: {e}")
        return HttpResponseRedirect("/a_addresult/")

@is_authenticated
@is_admin
def a_viewresult(request):
    results = Result.objects.all()
    return render(request, 'admin/a_viewresult.html', {'results': results})

@is_authenticated
@is_admin
def a_removeresult(request, result_id):
    try:
        result = Result.objects.get(id=result_id)
        result.file.delete()
        result.delete()
        messages.success(request, "Result deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete result: {e}")
    return HttpResponseRedirect("/a_viewresult/")

@is_authenticated
@is_admin
def a_addnotes(request):
    courses = Course.objects.all()
    return render(request, 'admin/a_addnotes.html', {'courses': courses})

@is_authenticated
@is_admin
def a_savenotes(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    try:
        title = request.POST.get('title')
        course_id = request.POST.get('course')
        notesfile = request.FILES['notesfile']
        created_by = request.user.username
        course = Course.objects.get(id=course_id)
        note = Notes.objects.create(
            title=title, file=notesfile,
            course=course, created_by=created_by
        )
        note.save()
        messages.success(request, "Notes uploaded successfully")
        return HttpResponseRedirect("/a_addnotes/")
    except Exception as e:
        messages.error(request, f"Failed to upload notes: {e}")
        return HttpResponseRedirect("/a_addnotes/")

@is_authenticated
@is_admin
def a_viewnotes(request):
    notes = Notes.objects.all()
    return render(request, 'admin/a_viewnotes.html', {'notes': notes})

@is_authenticated
@is_admin
def a_removenotes(request, notes_id):
    try:
        notes = Notes.objects.get(id=notes_id)
        notes.file.delete()
        notes.delete()
        messages.success(request, "Note deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete note: {e}")
    return HttpResponseRedirect("/a_viewnotes/")

@is_authenticated
@is_admin
def a_addcourse(request):
    teachers = Teacher.objects.all()
    departments = Course.DEPARTMENT_CHOICES
    return render(request, 'admin/a_addcourse.html', {
        'teachers': teachers,
        'departments': departments
    })

@is_authenticated
@is_admin
def a_savecourse(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    try:
        name = request.POST.get('name')
        code = request.POST.get('code')
        department = request.POST.get('department')
        year = request.POST.get('year')
        teacher_id = request.POST.get('teacher')
        teacher = Teacher.objects.get(id=teacher_id)
        course = Course.objects.create(
            name=name,
            code=code,
            department=department,
            year=year,
            teacher=teacher
        )
        course.save()
        messages.success(request, "Course added successfully")
        return HttpResponseRedirect("/a_addcourse/")
    except Exception as e:
        messages.error(request, f"Failed to add course: {e}")
        return HttpResponseRedirect("/a_addcourse/")

@is_authenticated
@is_admin
def a_managecourse(request):
    courses = Course.objects.all()
    return render(request, 'admin/a_managecourse.html', {'courses': courses})

@is_authenticated
@is_admin
def a_deletecourse(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        course.delete()
        messages.success(request, "Course deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete course: {e}")
    return HttpResponseRedirect("/a_managecourse/")

@is_authenticated
@is_admin
def a_addexam(request):
    courses = Course.objects.all()
    return render(request, 'admin/a_addexam.html', {'courses': courses})

@is_authenticated
@is_admin
def a_saveexam(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    try:
        course_id = request.POST.get('course')
        exam_type = request.POST.get('exam_type')
        exam_date = request.POST.get('exam_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        venue = request.POST.get('venue')
        course = Course.objects.get(id=course_id)
        exam = ExamSchedule.objects.create(
            course=course,
            exam_type=exam_type,
            exam_date=exam_date,
            start_time=start_time,
            end_time=end_time,
            venue=venue
        )
        exam.save()
        messages.success(request, "Exam schedule added successfully")
        return HttpResponseRedirect("/a_addexam/")
    except Exception as e:
        messages.error(request, f"Failed to add exam: {e}")
        return HttpResponseRedirect("/a_addexam/")

@is_authenticated
@is_admin
def a_viewexam(request):
    exams = ExamSchedule.objects.all().order_by('exam_date')
    return render(request, 'admin/a_viewexam.html', {'exams': exams})

@is_authenticated
@is_admin
def a_deleteexam(request, exam_id):
    try:
        exam = ExamSchedule.objects.get(id=exam_id)
        exam.delete()
        messages.success(request, "Exam deleted successfully")
    except Exception as e:
        messages.error(request, f"Failed to delete exam: {e}")
    return HttpResponseRedirect("/a_viewexam/")

@is_authenticated
@is_admin
def a_addfee(request):
    students = Student.objects.all()
    return render(request, 'admin/a_addfee.html', {'students': students})

@is_authenticated
@is_admin
def a_savefee(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    try:
        student_id = request.POST.get('student')
        semester = request.POST.get('semester')
        amount_due = request.POST.get('amount_due')
        amount_paid = request.POST.get('amount_paid')
        status = request.POST.get('status')
        due_date = request.POST.get('due_date')
        student = Student.objects.get(id=student_id)
        fee = FeeStatus.objects.create(
            student=student,
            semester=semester,
            amount_due=amount_due,
            amount_paid=amount_paid,
            status=status,
            due_date=due_date
        )
        fee.save()
        messages.success(request, "Fee record added successfully")
        return HttpResponseRedirect("/a_addfee/")
    except Exception as e:
        messages.error(request, f"Failed to add fee record: {e}")
        return HttpResponseRedirect("/a_addfee/")

@is_authenticated
@is_admin
def a_viewfee(request):
    fees = FeeStatus.objects.all().order_by('student', 'semester')
    return render(request, 'admin/a_viewfee.html', {'fees': fees})

@is_authenticated
@is_admin
def a_viewattendance(request):
    courses = Course.objects.all()
    selected_course = request.GET.get('course')
    attendance = None
    if selected_course:
        attendance = Attendance.objects.filter(
            course_id=selected_course
        ).order_by('date', 'student')
    return render(request, 'admin/a_viewattendance.html', {
        'courses': courses,
        'attendance': attendance,
        'selected_course': selected_course
    })

@is_authenticated
@is_admin
def a_viewmarks(request):
    courses = Course.objects.all()
    selected_course = request.GET.get('course')
    marks = None
    if selected_course:
        marks = InternalMarks.objects.filter(
            course_id=selected_course
        ).order_by('student', 'exam_type')
    return render(request, 'admin/a_viewmarks.html', {
        'courses': courses,
        'marks': marks,
        'selected_course': selected_course
    })

@is_authenticated
@is_admin
def prediction_page(request):
    result = None
    error = None
    if request.method == "POST":
        try:
            attendance = int(request.POST.get("attendance"))
            assignment = int(request.POST.get("assignment"))
            test = int(request.POST.get("test"))
            if model is None:
                error = "ML model not loaded"
            else:
                prediction = model.predict([[attendance, assignment, test]])
                result = "Student likely to PASS" if prediction[0] == 1 else "Student at risk"
        except Exception as e:
            error = f"Error in prediction: {e}"
    return render(request, "admin/prediction.html", {"result": result, "error": error})
