from django.shortcuts import render, redirect, get_object_or_404
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash



def is_admin(user):
    return user.is_authenticated and user.is_superuser



# Create your views here.
@user_passes_test(is_admin)
@login_required
def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('new_password2')
        is_superuser = request.POST.get('is_superuser') == 'true'

        # Basic validation
        if not username or not email or not password:
            messages.error(request, "All fields are required.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password, is_superuser=is_superuser)
            messages.success(request, f"User '{username}' registered successfully.")
            return redirect('users:users')

    return render(request, 'users/user_list.html') 




def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('users:dash')
            else:
                messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html', {'form': form})




@user_passes_test(is_admin)
@login_required
def users(request):
    users = User.objects.all()
    return render(request, 'users/user_list.html', {'users': users})


@login_required
def logout_view(request):
    logout(request)
    return redirect('users:login') 


@user_passes_test(is_admin)
@login_required
def disable_user(request, id):
    user = get_object_or_404(User, pk=id)
    if user.is_active:
        user.is_active = False
        user.save()
        messages.success(request, f"User: {user.username} has been deactivated.")
    else:
        messages.info(request, f"User: {user.username} is already inactive.")
    return redirect('users:users')



@user_passes_test(is_admin)
@login_required
def activate_user(request, id):
    user = get_object_or_404(User, pk=id)
    if user.is_active == False:
        user.is_active = True
        user.save()
        messages.success(request, f"User: {user.username} has been activated.")
    else:
        messages.info(request, f"User: {user.username} is already active.")
    return redirect('users:users') 


@login_required
def change_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)  # Keeps user logged in
        messages.success(request, 'Password changed successfully.')
        return redirect('users:user_list')  # or any other admin page
    return render(request, 'users/change_password.html', {'form': form})



@user_passes_test(is_admin)
@login_required
def update_user(request, pk):
    user = User.objects.get(pk=pk)
    form = UserCreateForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('users:user_list')
    return render(request, 'users/user_form.html', {'form': form})



@user_passes_test(is_admin)
@login_required
def delete_user(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('users:user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user})




@login_required
def dash(request):
    return render(request, "users/dash.html")

