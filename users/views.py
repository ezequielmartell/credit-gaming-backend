from django.core.mail import send_mail
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
# from accounts.models import CustomUser
from urllib.parse import urlencode
# from . import spotify
import requests
import time
import secrets
import string
from users.models import CustomUser
# Create your views here.


@api_view(['POST'])
def signup_view(request):
    data = request.data
    password = data.get('password')
    email = data.get('email').lower()

    try:
        validate_email(email)
    except ValidationError as error:
        return Response({'message': error}, status=400)
    
    if len(password) < 8:
        return Response({'message': 'Password must be at least 8 characters.'}, status=400)
    
    try:
        user = CustomUser.objects.create_user( email=email, password=password)
    except Exception as error:
        return Response({'message': f"Error creating user: {error}"}, status=400)

    login(request, user)
    send_mail(
        subject='Welcome to Skipify!', 
        message="Thank you for signing up! We are excited to have you on board.\n"
        "Please let us know if you have any questions or feedback.\n\n"
        f"Username: {email}\n"
        "Best,\nThe Skipify Team",
        from_email='bot@thinkmartell.com',
        recipient_list=[email], 
        fail_silently=False
        )
    return Response({'message': 'Successfully logged in.'})

@api_view(['POST'])
def login_view(request):
    data = request.data
    email = data.get('email')
    password = data.get('password')
        
    try:
        user = authenticate(username=email, password=password)
    except Exception as error:
        return Response({'message': error}, status=400)

    if user is None:
        return Response({'message': 'Invalid credentials.'}, status=400)

    login(request, user)
    return Response({'message': 'Successfully logged in.'})

@api_view(['GET'])
def logout_view(request):
    if not request.user.is_authenticated:
        return Response({'message': 'You\'re not logged in.'}, status=400)

    logout(request)
    return Response({'message': 'Successfully logged out.'})

@api_view(['GET'])
@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return Response({'isAuthenticated': False}, content_type='application/json')

    return Response({'isAuthenticated': True}, content_type='application/json')