from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                if user.is_superuser:
                    login(request, user)
                    return redirect('/')  # Superusers have access to everything
                elif user.is_staff and (user.is_enseignant or user.is_encadrant):
                    login(request, user)
                    return redirect('/')  # Regular staff members with roles
                else:
                    messages.error(request, "You do not have the required access privileges.")
            else:
                messages.error(request, "Your account is inactive. Please contact support.")
        else:
            messages.error(request, "Invalid Username or Password or Your account is inactive")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
