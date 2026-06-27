from rest_framework.routers import DefaultRouter
from .views import TraderViewSet

trader_router = DefaultRouter()
trader_router.register(r'users' , TraderViewSet)

users_urlpatterns = [
    *trader_router.urls
]