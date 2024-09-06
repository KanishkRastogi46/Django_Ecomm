from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login , logout , authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
import re

from .models import OtpModel
from . import generate_otp


# signup view
def signup(request):
    if request.method=="POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmpassword")
        username = firstname + " " + lastname

        username_regex = "^[a-zA-Z]+ [a-zA-Z]+$"
        email_regex = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if firstname.strip()=="" or lastname.strip()=="" or email.strip()=="" or password.strip()=="" or confirm_password.strip()=="":
            messages.error(request, "Please fill all the fields in signup form")
        elif password!=confirm_password:
            messages.error(request, "Your password didn't matched with confirm password")
        elif not re.findall(username_regex , username):
            messages.error(request, "Invalid username")
        elif re.findall(email_regex , email):
            messages.error(request, "Invalid email")
        else:
            user_exists = get_object_or_404(User , email=email)
            if user_exists:
                otp = OtpModel.objects.create(otp=generate_otp() , user_id=user_exists)
                otp.save()
                send_mail(
                    subject="EMAIL VERIFICATION",
                    message=f"your otp is {otp}",
                    from_email="rastogikanishk746@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=True
                )
                return redirect('verify')

            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.save()

            otp = OtpModel.objects.create(otp=generate_otp() , user_id=user)
            otp.save()
            
            send_mail(
                subject="EMAIL VERIFICATION",
                message=f"your otp is {otp}",
                from_email="",
                recipient_list=[user.email],
                fail_silently=True
            )
            return redirect("verify")

    return render(request , "eauth/signup.html")



# login view
def login(request):
    if request.method=="POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        email_regex = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if email.strip()=="" or password.strip()=="":
            messages.error(request, "Please fill all the fields in login form")
        elif not re.findall(email_regex , email):
            messages.error(request, "Invalid email")
        else:
            user = authenticate(request , email=email , password=password)
            if not user:
                messages.error(request, "Incorrect password")
            else:
                login(request , user)
                return redirect("home", user=user)
                    
    return render(request , "eauth/login.html")



# logout view
@login_required()
def logout(request):
    logout()
    return redirect('login')



# verify otp
def verify(request , email):
    if request.method=="POST":
        user = get_object_or_404(User , email=email)
        otp = OtpModel.objects.get(user_id=user)

        submitted_otp = request.POST.get("otp")

        if len(submitted_otp.strip())!=6:
            messages.error(request, "Invalid otp")
        else:
            if not otp.otp_is_valid(submitted_otp):
                messages.error(request, "Incorrect otp")
            else:
                return redirect('home')
    return render(request , "eauth/verify.html")