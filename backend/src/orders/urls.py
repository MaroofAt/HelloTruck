from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

order_router = DefaultRouter()
order_router.register(r'order' , OrderViewSet)


orders_urlpatterns = [
    *order_router.urls,

]