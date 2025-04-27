from rest_framework import serializers
from django.contrib.auth.models import User
import re
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .utils import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
PASSWORD_REGEX = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{12,}$"

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model=User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only':True}
        }
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'message':"Password fields didn't match."})
        if not re.match(PASSWORD_REGEX, attrs['password']):
            raise serializers.ValidationError({'message':"Password must be alphanumeric with special symbols and at least 12 characters long."})
        if not re.match(EMAIL_REGEX, attrs['email']):
            raise serializers.ValidationError({'message':"Email is not valid."})
        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'message':"Email or password is incorrect."})

        user = authenticate(username=user.username, password=password)
        if not user:
            raise serializers.ValidationError({'message':"Email or password is incorrect."})

        refresh = CustomTokenObtainPairSerializer.get_token(user)
        return {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }
    
class UserLogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist() 
        except Exception as e:
            raise serializers.ValidationError("Invalid or expired refresh token.")
        return {}