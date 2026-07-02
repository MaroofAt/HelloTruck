from rest_framework.permissions import BasePermission
from users.models import Credential  

class IsCaptain (BasePermission):
    def has_permission(self, request, view, *args):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.role == Credential.ROLE.CAPTAIN
    

class IsTrader (BasePermission):
     def has_permission(self, request, view, **args):
         if not request.user or not request.user.is_authenticated:
             return False
         
         return request.user.role == Credential.Role.TRADER
     

class IsAdmin (BasePermission):
     def has_permission(self, request , view, **args):
         if not request.user or not request.user.is_authenticated:
             return False
         
         return request.user.role == Credential.Role.ADMIN
     

class IsSubAdmin (BasePermission):
     def has_permission(self, request, view, **args):
         if not request.user or not request.user.is_authenticated:
             return False
         
         return request.user.role == Credential.Role.SUB_ADMIN