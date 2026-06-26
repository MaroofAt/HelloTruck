from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers

from users.models import Credential

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    role = serializers.ChoiceField(choices=Credential.Role.choices,required=True)
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    username_field = "identifier"

    def validate(self, attrs):
        credentials:Credential = authenticate(
            request=self.context.get("request"),
            role=attrs["role"],
            identifier=attrs["identifier"],
            password=attrs["password"],
        )

        if credentials is None:
            raise serializers.ValidationError(
                "Invalid credentials."
            )

        self.user = credentials
        refresh = self.get_token(credentials)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        data.update(credentials.jwt_claims())

        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer