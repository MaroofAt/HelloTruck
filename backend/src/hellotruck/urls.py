"""
URL configuration for hellotruck project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include

from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView
from drf_spectacular.utils import extend_schema , extend_schema_view

from tools.simplejwt import CustomTokenObtainPairView

from users.urls import users_urlpatterns
from dashboard.urls import dashboard_urlpatterns

simplejwt_auth_patterns = [
    path('token/',  extend_schema_view(
        post=extend_schema(
            tags=['Auth'],
            summary="Token",
            request={
                'application/json':{
                    'type':'object',
                    'properties':{
                        'role': {'type':'string', 'example':'trader'},
                        'identifier':{'type':'string', 'example':'m@m.com'},
                        'password':{'type':'string', 'example':'12345678'},
                    }
                }
            }
        ))(CustomTokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('users/token/refresh/', extend_schema_view(post=extend_schema(tags=['Auth'], summary="Refresh Token"))(TokenRefreshView.as_view()), name='token_refresh'),
]

api_patterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('users/', include(simplejwt_auth_patterns)),
    path('users/', include(users_urlpatterns)),
    path('dashboard/' , include(dashboard_urlpatterns)),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
]
