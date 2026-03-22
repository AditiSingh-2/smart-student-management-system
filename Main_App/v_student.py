from django.contrib import messages
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from Main_App.models import MyUser, Notes, Notification, Result, Student, Course, Attendance, InternalMarks, ExamSchedule, FeeStatus, Timetable
from Main_App.restrictions import is_authenticated, is_student

@is_authenticated
@is_student
def s_home(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        
        # Attendance warnings
        attendance_list = []
        courses = Course.objects.filter(department=student.department, year=student.year)
        for course in courses:
            total = Attendance.objects.filter(student=student, course=course).count()
            present = Attendance.objects.filter(student=student, course=course, is_present=True).count()
            if total > 0:
                percentage = (present / total) * 100
                attendance_list.append({
                    'course': course.name,
                    'percentage': round(percentage, 2),
                    'warning': percentage < 75
                })

        # Upcoming exams within 7 days
        from datetime import date, timedelta
        today = date.today()
        upcoming_exams = ExamSchedule.objects.filter(
            course__department=student.department,
            exam_date__range=[today, today + timedelta(days=7)]
        )

        # Fee status
        fee = FeeStatus.objects.filter(student=student).last()

        context = {
            'student': student,
            'attendance_list': attendance_list,
            'upcoming_exams': upcoming_exams,
            'fee': fee,
        }
        return render(request, 'student/s_home.html', context)
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_student
def s_profile(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        return render(request, 'student/s_profile.html', {'student': student})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_student
def s_saveprofile(request):
    if request.method != "POST":
        return HttpResponse("Method not Allowed..!")
    student_id = request.POST.get('student_id')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')
    email = request.POST.get('email')
    address = request.POST.get('address')
    gender = request.POST.get('gender')
    phone = request.POST.get('phone')
    password = request.POST.get('password')
    try:
        user = MyUser.objects.get(id=student_id)
        user.first_name = firstname
        user.last_name = lastname
        user.email = email
        if password is not None and password != "":
            user.set_password(password)
        user.save()
        student = Student.objects.get(admin=student_id)
        student.address = address
        student.gender = gender
        student.phone = phone
        student.save()
        messages.success(request, "Profile updated successfully")
        return HttpResponseRedirect('/studentprofile/')
    except Exception as e:
        messages.error(request, f"Failed to update profile: {e}")
        return HttpResponseRedirect('/studentprofile/')

@is_authenticated
@is_student
def s_viewresult(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        results = Result.objects.filter(course__department=student.department)
        return render(request, 'student/s_viewresult.html', {'results': results})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_student
def s_viewnotification(request):
    notifications = Notification.objects.all()
    return render(request, 'student/s_viewnotification.html', {'notifications': notifications})

@is_authenticated
@is_student
def s_viewnotes(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        notes = Notes.objects.filter(course__department=student.department)
        return render(request, 'student/s_viewnotes.html', {'notes': notes})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_student
def s_viewattendance(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        courses = Course.objects.filter(department=student.department, year=student.year)
        attendance_data = []
        for course in courses:
            total = Attendance.objects.filter(student=student, course=course).count()
            present = Attendance.objects.filter(student=student, course=course, is_present=True).count()
            percentage = round((present / total) * 100, 2) if total > 0 else 0
            attendance_data.append({
                'course': course,
                'total': total,
                'present': present,
                'percentage': percentage,
                'warning': percentage < 75
            })
        return render(request, 'student/s_attendance.html', {'attendance_data': attendance_data})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_student
def s_viewmarks(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        marks = InternalMarks.objects.filter(student=student)
        return render(request, 'student/s_marks.html', {'marks': marks})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_student
def s_viewexams(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        exams = ExamSchedule.objects.filter(
            course__department=student.department
        ).order_by('exam_date')
        return render(request, 'student/s_exams.html', {'exams': exams})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_student
def s_viewfees(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        fees = FeeStatus.objects.filter(student=student).order_by('semester')
        return render(request, 'student/s_fees.html', {'fees': fees})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')

@is_authenticated
@is_student
def s_viewtimetable(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        timetable = Timetable.objects.filter(
            course__department=student.department,
            course__year=student.year
        ).order_by('day', 'start_time')
        return render(request, 'student/s_timetable.html', {'timetable': timetable})
    except Exception as e:
        return HttpResponse(f'<h1>Error: {e}</h1>')
