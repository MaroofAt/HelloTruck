from rest_framework.routers import DefaultRouter
from .views import OrderViewSet , TripViewSet , SpecialShipmentViewSet

order_router = DefaultRouter()
order_router.register(r'order' , OrderViewSet)

trip_router = DefaultRouter()
trip_router.register(r'trip' , TripViewSet)

special_shipment_router = DefaultRouter()
special_shipment_router.register(r'special_shipment' , SpecialShipmentViewSet)

orders_urlpatterns = [
    *order_router.urls,
    *trip_router.urls,
    *special_shipment_router.urls,

]