from rest_framework.routers import DefaultRouter
from .views import OrderViewSet , TripViewSet

order_router = DefaultRouter()
order_router.register(r'order' , OrderViewSet)

trip_router = DefaultRouter()
trip_router.register(r'trip' , TripViewSet)

orders_urlpatterns = [
    *order_router.urls,
    *trip_router.urls,

]