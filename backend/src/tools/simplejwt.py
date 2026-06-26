from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import Credential

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom data to the response
        credentials:Credential = self.user

        data.update(credentials.jwt_claims())
        
        # Add custom claims to the token itself (optional)
        # refresh = self.get_token(self.user)
        # refresh['custom_claim'] = 'custom_value'
        # refresh['user_role'] = getattr(self.user, 'role', 'user')
        
        return data
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['role'] = user.role

        return token


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer