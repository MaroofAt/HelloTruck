from rest_framework.routers import DefaultRouter
from .views import TraderViewSet, CaptainViewSet, Sub_AdminViewSet

trader_router = DefaultRouter()
trader_router.register(r'traders' , TraderViewSet)
captain_router = DefaultRouter()
captain_router.register(r'captains' , CaptainViewSet)
sub_admin_router = DefaultRouter()
sub_admin_router.register(r'sub_admins' , Sub_AdminViewSet)

users_urlpatterns = [
    *trader_router.urls,
    *captain_router.urls,
    *sub_admin_router.urls,
]