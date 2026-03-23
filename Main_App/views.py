from django.shortcuts import render
from django.contrib import messages
from Main_App.EmailAuthentication import EmailAuth
from django.contrib.auth import authenticate, login, logout
from django.http.response import HttpResponse, HttpResponseRedirect

def loginpage(request):
    return render(request,'loginpage.html')

def loginuser(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method not allowed</h2>")
    else:
        user = EmailAuth.authenticate(
            request,
            username=request.POST.get('email'),
            password=request.POST.get('password')
        )
        if user is not None:
            login(request, user)
            if user.user_type == '1':
                return HttpResponseRedirect('/adminhome/')
            elif user.user_type == '2':
                return HttpResponseRedirect('/teacherhome/')
            elif user.user_type == '3':
                return HttpResponseRedirect('/studenthome/')
            else:
                return HttpResponse(f"Invalid user type: {user.user_type}")
        else:
            messages.error(request, "Invalid login details..!")
            return HttpResponseRedirect("/")

def logoutuser(request):
    logout(request)
    return HttpResponseRedirect('/') 
