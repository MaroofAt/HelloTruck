from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import extend_schema, OpenApiExample

from django.utils import timezone
from django.db.models import Prefetch
from django.db import transaction
from datetime import timedelta
from secrets import compare_digest

from tools.permissions import IsTrader , IsAdmin , IsSubAdmin , IsCaptain 
from tools.responses import method_not_allowed, exception_response

from .models import Credential, Trader, Captain, Sub_Admin , User_OTP , Vehicle
from orders.models import Trip, Order_Load

from .serializers import TraderRegisterSerializer, CaptainRegisterSerializer, Sub_AdminSerializer , VehicleSerializer, CaptainTripListSerializer
from .utils import send_otp_by_sms , send_otp_email_to_user

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
        tags=["Users", "Traders"],
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
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return exception_response(e)

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
    
    @extend_schema(
        summary="Send OTP trader",
        operation_id="send_otp_trader",
        description="sending otp for the specified trader mobile phone or email in the request (to check that the user is the mobile phone owner) ",
        tags=["Users", "Traders"],
    )
    @action(detail=False , methods=['post'] , serializer_class=TraderRegisterSerializer )
    def send_otp_trader(self , request):
        mobile_number = request.data.get('mobile_number')
        email = request.data.get('email') 
        # if not mobile_number:
        #     return Response(
        #         {'error': 'mobile number is required'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            if not email:
                print("/////////////////////////////////////")
                send_otp_by_sms(mobile_number)
            elif not mobile_number:
                send_otp_email_to_user(email)

            return Response(
                {'message': 'OTP has been sent to your mobile number'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors , status = status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Verify Trader Register",
        operation_id="verify_trader_register",
        description="Verify Trader Register API",
        tags=["Users", "Traders"],
        examples=[
            OpenApiExample(
                'Request Body [Email]',
                value={
                    'email': 'm@m.com',
                    'password': '12345678',
                    'ecommerce': False,
                    'name': 'mmm',
                    'otp': "123456"
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
                    'otp': "123456"

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
    @action(detail=False, methods=['post'], serializer_class=TraderRegisterSerializer)
    def verify_trader_register(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            otp = request.data.get('otp')
            if not email:
                return Response(
                    {'error': 'Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not otp:
                return Response(
                    {'error': 'OTP is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            old_otps = User_OTP.objects.filter(expires_at__lt = timezone.now()).delete()
            
            if not User_OTP.objects.filter(otp=otp).exists():
                return Response(
                    {'error': 'OTP Does Not Match'},
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )
            
            table_otp = User_OTP.objects.get(otp=otp)
            if table_otp.created_at < timezone.now() - timedelta(minutes=5):
                table_otp.delete()
                return Response(status=status.HTTP_410_GONE)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return exception_response(e)
    
class CaptainViewSet(ModelViewSet):
    queryset = Captain.objects.all()
    serializer_class = CaptainRegisterSerializer #TODO change to Captain Serializer later

    def get_permissions(self):
        return super().get_permissions()
    def get_queryset(self):
        return super().get_queryset()

    @extend_schema(
        summary="List authenticated Captain trips",
        operation_id="list_captain_trips",
        description="Returns only trips assigned to the authenticated Captain's vehicles.",
        tags=["Users", "Captains"],
        responses={200: CaptainTripListSerializer(many=True)},
    )
    @action(
        detail=False,
        methods=['get'],
        serializer_class=CaptainTripListSerializer,
        permission_classes=[IsAuthenticated, IsCaptain],
    )
    def list_captain_trips(self, request):
        captain = Captain.objects.get(credentials=request.user)
        captain_loads = Order_Load.objects.filter(
            vehicle__captain=captain
        ).select_related(
            'vehicle',
            'order',
            'order__from_location',
            'order__to_location',
            'order__from_branch',
            'order__to_branch',
        ).order_by('id')
        trips = Trip.objects.filter(
            order_loads__vehicle__captain=captain
        ).distinct().prefetch_related(
            Prefetch(
                'order_loads',
                queryset=captain_loads,
                to_attr='captain_order_loads',
            )
        ).order_by('launch_datetime', 'id')

        serializer = self.get_serializer(trips, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Captain Register",
        operation_id="captain_register",
        description="Captain Register API",
        tags=["Users", "Captains"],
        examples=[
            OpenApiExample(
                'Request Body [Username]',
                value={
                    'username': 'username',
                    'password': '12345678',
                    'latitude': 38.8951,
                    'longitude': 77.0364,
                    'name': 'mmm',
                },
                request_only=True
            ),
            OpenApiExample(
                'Request Body [Mobile]',
                value={
                    'mobile_number': '0987654321',
                    'password': '12345678',
                    'latitude': 38.8951,
                    'longitude': 77.0364 ,
                    'name': 'mmmmm',
                },
                request_only=True
            ),
            OpenApiExample(
                '201 Response Body',
                value={
                    'accommodation_id': 1,
                    'permanent': False,
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
    @action(detail=False, methods=['post'], serializer_class=CaptainRegisterSerializer, url_path='register')
    def register(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return exception_response(e)

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
    
    @extend_schema(
        summary="Send OTP Captain",
        operation_id="send_otp_captain",
        description="sending otp for the specified captain mobile phone or email in the request (to check that the user is the mobile phone owner) ",
        tags=["Users", "Captains"],
    )
    @action(detail=False , methods=['post'] , serializer_class=CaptainRegisterSerializer )
    def send_otp_captain(self , request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile_number = serializer.validated_data.get('mobile_number')
        if not mobile_number:
            return Response(
                {'error': 'mobile_number is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        purpose = 'captain_registration'
        User_OTP.objects.filter(
            mobile_number=mobile_number,
            purpose=purpose,
        ).delete()
        sent, _ = send_otp_by_sms(mobile_number, purpose=purpose)
        if not sent:
            return Response(
                {'error': 'Unable to send OTP. Please try again.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {'message': 'OTP has been sent to your mobile number'},
            status=status.HTTP_200_OK,
        )
   
    @extend_schema(
        summary="Verify Captain Register",
        operation_id="verify_captain_register",
        description="Captain Register API",
        tags=["Users", "Captains"],
        examples=[
            OpenApiExample(
                'Request Body [Username]',
                value={
                    'username': 'username',
                    'password': '12345678',
                    'latitude': 38.8951,
                    'longitude': 77.0364,
                    'name': 'mmm',
                    'otp': "123456"
                },
                request_only=True
            ),
            OpenApiExample(
                'Request Body [Mobile]',
                value={
                    'mobile_number': '0987654321',
                    'password': '12345678',
                    'latitude': 38.8951,
                    'longitude': 77.0364 ,
                    'name': 'mmmmm',
                    'otp': "123456"
                },
                request_only=True
            ),
            OpenApiExample(
                '201 Response Body',
                value={
                    'accommodation_id': 1,
                    'permanent': False,
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
    @action(detail=False, methods=['post'], serializer_class=CaptainRegisterSerializer)
    def verify_captain_register(self, request, *args, **kwargs):
        try:
            otp = request.data.get('otp')
            if not otp:
                return Response(
                    {'error': 'OTP is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            mobile_number = serializer.validated_data.get('mobile_number')
            if not mobile_number:
                return Response(
                    {'error': 'mobile_number is required'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                table_otp = User_OTP.objects.select_for_update().filter(
                    mobile_number=mobile_number,
                    purpose='captain_registration',
                ).first()
                if table_otp is None or not compare_digest(
                    table_otp.otp or '',
                    str(otp),
                ):
                    return Response(
                        {'error': 'OTP Does Not Match'},
                        status=status.HTTP_406_NOT_ACCEPTABLE,
                    )
                if table_otp.expires_at <= timezone.now():
                    table_otp.delete()
                    return Response(
                        {'error': 'OTP has expired'},
                        status=status.HTTP_410_GONE,
                    )

                serializer.save()
                table_otp.delete()

                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            return exception_response(e)
class Sub_AdminViewSet(ModelViewSet):
    queryset = Sub_Admin.objects.all()
    serializer_class = Sub_AdminSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.action == 'create':
            self.permission_classes.append(IsAuthenticated)
            self.permission_classes.append(IsAdminUser)
        return super().get_permissions()
    def get_queryset(self):
        return super().get_queryset()

    @extend_schema(
        summary="Create Sub_Admin",
        operation_id="create_sub_admin",
        description="Create Sub_Admin API",
        tags=["Users", "Sub_Admin"],
        examples=[
            OpenApiExample(
                'Request Body',
                value={
                    'email': 'm@m.coom',
                    'password': '12345678',
                    'branch': 1,
                    'name': 'mmm',
                },
                request_only=True
            ),
            OpenApiExample(
                '201 Response Body',
                value={
                    'branch': 1,
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
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    @extend_schema(exclude=True)
    def list(self, request, *args, **kwargs):
        return method_not_allowed()
        return super().list(request, *args, **kwargs)
    @extend_schema(exclude=True)
    def retrieve(self, request, *args, **kwargs):
        return method_not_allowed()
        return super().retrieve(request, *args, **kwargs)
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


class VehicleViewSet(ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated ]


    def get_permissions(self):
        if self.action == "create_vehicle":
            print("/////////////////////////////////////////////////////////////////////////")
            if self.request.user.is_authenticated and self.request.user.role != Credential.Role.ADMIN:
                if self.request.user.role != Credential.Role.SUB_ADMIN:
                    self.permission_classes.append(IsCaptain)
                else:
                    self.permission_classes.append(IsSubAdmin) 
        return super().get_permissions()

    @extend_schema(
        summary="Create Vehicle",
        operation_id= "create_vehicle",
        description= "captain or sub_admin or admin want to vehicle",
        tags=["Vehicle"],
        request={
            'application/json':{
                'type': 'object',
                'properties' : {
                    "type":{'type':'string' , 'example':'a' },
                    "accepted_volume":{'type':'double' , 'example': 1.5 },
                    "fuel_consumption_per_1km":{'type': "double" , 'example': "0.5" },
                    "feul_type":{'type': 'string' ,'example':"a" },
                    "verified":{'type': 'boolean', 'example':True },
                    "delivery":{'type': 'boolean', 'example':False },
                    "captain":{'type': 'integer' , 'example': '1' }
                }
            }
        }
    )
    @action(detail=False , methods=["post"] , serializer_class = VehicleSerializer)
    def create_vehicle(self, request, *args, **kwargs):
        # serializer =
        return super().create(request, *args, **kwargs)
