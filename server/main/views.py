from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

def home(request):
    """Serve the index.html page as homepage"""
    return render(request, 'index.html')

def login_view(request):
    """Handle login page and authentication"""
    if request.method == 'POST':
        # Handle AJAX login request
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                email = data.get('email')
                password = data.get('password')
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON'})
        else:
            # Handle form submission
            email = request.POST.get('email')
            password = request.POST.get('password')
        
        # Try to find user by email (Django uses username by default)
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': 'Invalid email or password'})
            messages.error(request, 'Invalid email or password')
            return render(request, 'login.html')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'redirect_url': '/chatbot/'})
            return redirect('main:chatbot')
        else:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'error': 'Invalid email or password'})
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'login.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('main:home')

@login_required
def chatbot_view(request):
    """Serve the chatbot page (only accessible after login)"""
    return render(request, 'chatbot.html', {'user': request.user})
