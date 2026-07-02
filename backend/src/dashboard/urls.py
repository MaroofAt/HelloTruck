from rest_framework.routers import DefaultRouter
from .views import BranchViewSet

branch_router = DefaultRouter()
branch_router.register(r'branch' , BranchViewSet)


dashboard_urlpatterns = [
    *branch_router.urls,

]