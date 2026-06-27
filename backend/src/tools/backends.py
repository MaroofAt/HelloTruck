from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from tools.models import normalize_mobile_number

from users.models import Credential

class EmailOrMobileBackend(ModelBackend):
    def authenticate(self, request, role='trader', identifier = None, password = None, **kwargs):
        try:
            queryset = Credential.objects.filter(role=role)
            if role == Credential.Role.TRADER:
                queryset = queryset.filter(
                    Q(email=identifier) |
                    Q(mobile_number=normalize_mobile_number(identifier))
                )

            elif role == Credential.Role.CAPTAIN:
                queryset = queryset.filter(
                    Q(username=identifier) |
                    Q(mobile_number=normalize_mobile_number(identifier))
                )

            elif role == Credential.Role.SUB_ADMIN:
                queryset = queryset.filter(
                    email=identifier
                )

            else:
                return None

            user = queryset.first()

            if user is None:
                return None

            if user.check_password(password):
                return user

            return None

        except Credential.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return Credential.objects.get(pk=user_id)
        except Credential.DoesNotExist:
            return None
    
