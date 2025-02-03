from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from django.db.models import Q



@api_view(['POST'])
def register_user(request):
    """Register a new user"""
    data = request.data

    if CustomUser.objects.filter(username=data['username']).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = CustomUser.objects.create(
        username=data['username'],
        email=data['email'],
        password=make_password(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        affiliation=data.get('affiliation', None),
        is_active=True
    )
    serializer = UserSerializer(user)
    return Response({'message': 'User registered successfully', 'user': serializer.data}, status=status.HTTP_201_CREATED)

@api_view(["POST"])
def login_user(request):
    """Login user and return token"""
    data = request.data
    user_identifier = data.get("username")  # This can be email or username
    password = data.get("password")

    try:
        # Try to fetch user by username or email
        user = CustomUser.objects.filter(Q(username=user_identifier) | Q(email=user_identifier)).first()

        if user and user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({"message": "Login successful", "token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
    
    except CustomUser.DoesNotExist:
        return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_users(request):
    """Retrieve all users"""
    users = CustomUser.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
