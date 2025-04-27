from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

class CustomTokenObtainPairSerializer(serializers.Serializer):
    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)

        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff

        return token
    
