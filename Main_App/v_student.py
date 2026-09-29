import os
from google_auth_oauthlib.flow import Flow
from Main_App.gmail_service import get_gmail_flow, get_gmail_service, fetch_emails, get_auth_url
from Main_App.email_classifier import classify_email
from Main_App.models import StudentEmailToken
import json
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

@is_authenticated
@is_student
def s_connect_gmail(request):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    flow = get_gmail_flow()
    auth_url, state = get_auth_url(flow)
    request.session['code_verifier'] = flow.code_verifier
    request.session['gmail_state'] = state
    # Store flow state in session
    
    request.session['gmail_user_id'] = request.user.id
    return HttpResponseRedirect(auth_url)
    print("AUTH URL:", auth_url)


def gmail_callback(request):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    try:
        state = request.session.get('gmail_state')
        code_verifier = request.session.get('code_verifier')
        flow = Flow.from_client_secrets_file(
            'credentials.json',
            scopes=['https://www.googleapis.com/auth/gmail.readonly'],
            redirect_uri='http://127.0.0.1:8000/gmail_callback/',
            state=state
        )
        flow.code_verifier = code_verifier
        flow.fetch_token(
            authorization_response=request.build_absolute_uri()
        )
        
        creds = flow.credentials
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': list(creds.scopes)
        }
        
        user_id = request.session.get('gmail_user_id')

        if not user_id:
            return HttpResponse("Session expired. Please login again.")

        student = Student.objects.get(admin=user_id)
        StudentEmailToken.objects.update_or_create(
            student=student,
            defaults={'token_data': json.dumps(token_data)}
        )
        
        messages.success(request, "Gmail connected successfully!")
        return HttpResponseRedirect('/s_emails/')
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

@is_authenticated
@is_student
def s_emails(request):
    try:
        student = Student.objects.get(admin=request.user.id)
        
        # Check if Gmail is connected
        try:
            token_obj = StudentEmailToken.objects.get(student=student)
            token_data = json.loads(token_obj.token_data)
        except StudentEmailToken.DoesNotExist:
            return render(request, 'student/s_emails.html', {
                'gmail_connected': False
            })
        
        # Fetch emails
        service, creds = get_gmail_service(token_data)
        
        # Update token if refreshed
        new_token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': list(creds.scopes)
        }
        token_obj.token_data = json.dumps(new_token_data)
        token_obj.save()
        
        emails = fetch_emails(service, max_results=50)
        
        # Classify each email
        classified_emails = []
        for email in emails:
            try:
                classification = classify_email(
                    email['subject'],
                    email['sender'],
                    email['body']
                )
                classified_emails.append({
                    'email': email,
                    'classification': classification
                })
            except Exception as e:
                print("CLASSIFICATION ERROR:", e)
                import traceback
                traceback.print_exc()

                classified_emails.append({
                    'email': email,
                    'classification': {
                        'priority': 'LOW',
                        'summary': 'Could not classify',
                        'deadline': None,
                        'reason': str(e)
                    }
               })                    
                
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        classified_emails.sort(
            key=lambda x: priority_order.get(
                x['classification']['priority'], 4
            )
        )
        
        return render(request, 'student/s_emails.html', {
            'gmail_connected': True,
            'classified_emails': classified_emails
        })
    except Exception as e:
        print("OUTER ERROR:", e)
        import traceback
        traceback.print_exc()

        return render(request, 'student/s_emails.html', {
            'gmail_connected': False,
            'error': str(e)
        })
       