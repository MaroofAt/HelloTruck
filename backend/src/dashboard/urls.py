from rest_framework.routers import DefaultRouter
from .views import BranchViewSet , LocationViewSet

branch_router = DefaultRouter()
branch_router.register(r'branch' , BranchViewSet)

location_router = DefaultRouter()
location_router.register(r"location", LocationViewSet)


dashboard_urlpatterns = [
    *branch_router.urls,
    *location_router.urls,

]