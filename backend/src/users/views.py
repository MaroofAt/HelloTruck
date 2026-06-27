from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from drf_spectacular.utils import extend_schema, OpenApiExample

from tools.responses import method_not_allowed, exception_response

from .models import Credential, Trader
from .serializers import TraderRegisterSerializer

# Create your views here.
class TraderViewSet(ModelViewSet):
    queryset = Trader.objects.all()
    serializer_class = TraderRegisterSerializer #TODO change to Trader Serializer later

    def get_permissions(self):
        return super().get_permissions()
    def get_queryset(self):
        return super().get_queryset()

    @extend_schema(
        summary="Trader Register",
        operation_id="trader_register",
        description="Trader Register API",
        tags=["Users"],
        examples=[
            OpenApiExample(
                'Request Body [Email]',
                value={
                    'email': 'm@m.com',
                    'password': '12345678',
                    'ecommerce': False,
                    'name': 'mmm',
                },
                request_only=True
            ),
            OpenApiExample(
                'Request Body [Mobile]',
                value={
                    'mobile_number': '0987654321',
                    'password': '12345678',
                    'ecommerce': False,
                    'name': 'mmmmm',
                },
                request_only=True
            ),
            OpenApiExample(
                '201 Response Body',
                value={
                    'ecommerce': False,
                    'name': 'abbas',
                    'credentials': {
                        'identifier': 'm@m.com',
                        'identifier_type': 'email',
                    }
                },
                response_only=True
            )
        ]
    )
    @action(detail=False, methods=['post'], serializer_class=TraderRegisterSerializer, url_path='register')
    def register(self, request, *args, **kwargs):
        # try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        # except Exception as e:
        #     return exception_response(e)

    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        return method_not_allowed()
        return super().list(request, *args, **kwargs)
    @extend_schema(exclude=True)
    def retrieve(self, request, *args, **kwargs):
        return method_not_allowed()
        return super().retrieve(request, *args, **kwargs)
    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return method_not_allowed()
        return super().create(request, *args, **kwargs)
    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        return method_not_allowed()
        return super().update(request, *args, **kwargs)
    @extend_schema(exclude=True)
    def partial_update(self, request, *args, **kwargs):
        return method_not_allowed()
        return super().partial_update(request, *args, **kwargs)
    @extend_schema(exclude=True)
    def destroy(self, request, *args, **kwargs):
        return method_not_allowed()
        return super().destroy(request, *args, **kwargs)