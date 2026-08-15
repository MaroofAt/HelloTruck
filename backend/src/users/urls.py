from rest_framework.routers import DefaultRouter
from .views import TraderViewSet, CaptainViewSet, Sub_AdminViewSet , VehicleViewSet , DiscountViewSet

trader_router = DefaultRouter()
trader_router.register(r'traders' , TraderViewSet)
captain_router = DefaultRouter()
captain_router.register(r'captains' , CaptainViewSet)
sub_admin_router = DefaultRouter()
sub_admin_router.register(r'sub_admins' , Sub_AdminViewSet)
vehicle_router = DefaultRouter()
vehicle_router.register(r'vehicles' , VehicleViewSet)
discount_router = DefaultRouter()
discount_router.register(r'discount' , DiscountViewSet)

users_urlpatterns = [
    *trader_router.urls,
    *captain_router.urls,
    *sub_admin_router.urls,
    *vehicle_router.urls,
    *discount_router.urls,
]