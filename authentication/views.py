from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    try:
        return user.userprofile.is_admin
    except:
        return False

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('dashboard:dashboard')
                else:
                    messages.error(request, 'Your account is disabled. Please contact the administrator.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please enter both username and password.')
    
    return render(request, 'authentication/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.all().select_related('userprofile')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_user':
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')
            role = request.POST.get('role')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                profile = user.userprofile
                profile.role = role
                profile.phone = phone
                profile.address = address
                profile.save()
                
                messages.success(request, f'User {username} created successfully.')
                return redirect('authentication:manage_users')
    
    return render(request, 'authentication/manage_users.html', {'users': users})

@login_required
@user_passes_test(is_admin)
@require_POST
def toggle_user_status(request):
    user_id = request.POST.get('user_id')
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        return JsonResponse({
            'success': True, 
            'message': f'User {user.username} {status} successfully.',
            'is_active': user.is_active
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'})

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        profile = user.userprofile
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('authentication:profile')
    
    return render(request, 'authentication/profile.html')
