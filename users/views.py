from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response 
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserLogoutSerializer
from rest_framework.views import APIView

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'User registered successfuly'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            response = Response(
                {
                    "message": "Login successful.",
                    "refresh_token":serializer.validated_data['refresh_token'],
                    "access_token":serializer.validated_data['access_token']
                    },
                    status=status.HTTP_200_OK)
            response['Authorization'] = f"Bearer {serializer.validated_data['access_token']}"
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    def delete(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)