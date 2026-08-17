from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.exceptions import ValidationError

from drf_spectacular.utils import extend_schema, OpenApiExample

from django.utils import timezone 
from datetime import timedelta

from tools.permissions import IsTrader , IsAdmin , IsSubAdmin , IsCaptain 
from tools.responses import method_not_allowed, exception_response

from .models import Credential, Trader, Captain, Sub_Admin , User_OTP , Vehicle , Discount , Discount_Traders
from .serializers import TraderRegisterSerializer, CaptainRegisterSerializer, Sub_AdminSerializer , VehicleSerializer ,ListCaptainTripsSerializer , CaptainSerializer , DiscountSerializer , AddDiscountToTraderSerializer ,ListDiscountSerializer
from .utils import send_otp_by_sms , send_otp_email_to_user


# Create your views here.
class TraderViewSet(ModelViewSet):
    queryset = Trader.objects.all()
    serializer_class = TraderRegisterSerializer #TODO change to Trader Serializer later

    def get_permissions(self):
        if self.action == "show_trader_discount":
            self.permission_classes = [IsTrader]
        if self.action == "list":
            self.permission_classes = [IsAdmin]
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

    @extend_schema(
        summary="List Trader",
        operation_id="list_trader",
        description="Admin Want to See trader",
        tags=["Traders"],
    )
    def list(self, request, *args, **kwargs):
        # return method_not_allowed()
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
        
    @extend_schema(
        summary="Show Trader Discount",
        operation_id="show_trader_discount",
        description="Trader Want to See his Discount",
        tags=["Traders"],
    )
    @action(detail=False , methods=["GET"] )
    def show_trader_discount(self, request, *args, **kwargs):
        credential = Credential.objects.filter(id=request.user.id).first()
        trader = Trader.objects.filter(credentials=credential.id).first()
        discount_traders = Discount_Traders.objects.filter(trader=trader.id)

        if not discount_traders.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)

        discount_ids = discount_traders.values_list('discount_id', flat=True)
        discounts = Discount.objects.filter(id__in=discount_ids)

        serializer = DiscountSerializer(discounts, many=True)
        return Response({
            "detail": "Congratulations! You have discounts.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

        # if discount_trader.exists():
        #     # discount_trader = discount_trader.first()
        #     discount = Discount.objects.filter(id=discount_trader.discount.id)
        #     return Response({
        #         "detail": "Congratulations You Have Discount",
        #         "data": discount,
        #     } , status.HTTP_200_OK)
        # return Response(status.HTTP_204_NO_CONTENT)

    
class CaptainViewSet(ModelViewSet):
    queryset = Captain.objects.all()
    serializer_class = CaptainSerializer
    # serializer_class = CaptainRegisterSerializer #TODO change to Captain Serializer later

    def get_permissions(self):
        if self.action == "list_captain_trips":
            self.permission_classes.append(IsCaptain)
        if self.action == "list_captain":
            if self.request.user.is_authenticated and self.request.user.role != Credential.Role.ADMIN:
                self.permission_classes.append(IsSubAdmin) 
            self.permission_classes.append(IsAdmin) 
            

        return super().get_permissions()
    def get_queryset(self):
        return super().get_queryset()

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
            serializer = CaptainRegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return exception_response(e)

    @extend_schema(
        summary="List Captain",
        operation_id="list_captain",
        description="List all captains ",
        tags=["Captains"],
    )
    # @action(detail=True, methods=["get"], serializer_class=CaptainSerializer)
    def list(self, request, *args, **kwargs):
        # return method_not_allowed()
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
        mobile_number = request.data.get('mobile_number')
        email = request.data.get('email') 
        # if not mobile_number:
        #     return Response(
        #         {'error': 'mobile number is required'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            # if not email:
            #     print("/////////////////////////////////////")
            send_otp_by_sms(mobile_number)
            # elif not mobile_number:
            #     send_otp_email_to_user(email)

            return Response(
                {'message': 'OTP has been sent to your mobile number'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors , status = status.HTTP_400_BAD_REQUEST)
   
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
            mobile_number = request.data.get('mobile_number')
            otp = request.data.get('otp')
            if not mobile_number:
                return Response(
                    {'error': 'mobile_number is required'},
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

    @extend_schema(
        summary="List Captain Trips",
        operation_id= "list_captain_trips",
        description= "captain want to see his trips",
        tags=["Captains"],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties': {
                    # "status": {'type':"string" ,
                    #         'enum': ["pending" , "launched" , "delivered" ] ,
                    #         "example": 'launched'
                    # },
                }
            }
        } 
    )
    @action(detail=False , methods=["GET"] , serializer_class = ListCaptainTripsSerializer )
    def list_captain_trips(self, request , *args, **kwargs):
        data = request.data.copy()
        data["id"] = request.user.id
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors , status.HTTP_400_BAD_REQUEST)
    
class Sub_AdminViewSet(ModelViewSet):
    queryset = Sub_Admin.objects.all()
    serializer_class = Sub_AdminSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.action == 'create' or self.action == 'list':
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
    @extend_schema(
        summary="List Sub Admin",
        operation_id= "list_sub_admin",
        description= "admin want to List Sub Admin",
        tags=["Sub_Admin"],
    )
    def list(self, request, *args, **kwargs):
        # return method_not_allowed()
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
            if self.action == "list_vehicle":
                if self.request.user.is_authenticated and self.request.user.role != Credential.Role.ADMIN:
                    self.permission_classes.append(IsSubAdmin) 
                self.permission_classes.append(IsAdmin) 
        return super().get_permissions()

    @extend_schema(
        summary="Create Vehicle",
        operation_id= "create_vehicle",
        description= "captain or sub_admin or admin want to create vehicle",
        tags=["Vehicle"],
        request={
            'application/json':{
                'type': 'object',
                'properties' : {
                    "type":{'type':'string' , 'example':'light_truck' },
                    "accepted_volume":{'type':'double' , 'example': 1.5 },
                    "fuel_consumption_per_1km":{'type': "double" , 'example': "0.5" },
                    "fuel_type ":{'type': 'string' ,'example':"gasoline" },
                    "verified":{'type': 'boolean', 'example':True },
                    "delivery":{'type': 'boolean', 'example':False },
                    "captain":{'type': 'integer' , 'example': '1' },
                    'image': {'type': 'string' , 'format': 'binary'}
                }
            },
            'multipart/form-data':{
                'type': 'object',
                'properties' : {
                    "type":{'type':'string' , 'example':'light_truck' },
                    "accepted_volume":{'type':'double' , 'example': 1.5 },
                    "fuel_consumption_per_1km":{'type': "double" , 'example': "0.5" },
                    "fuel_type ":{'type': 'string' ,'example':"gasoline" },
                    "verified":{'type': 'boolean', 'example':True },
                    "delivery":{'type': 'boolean', 'example':False },
                    "captain":{'type': 'integer' , 'example': '1' },
                    'image': {'type': 'string' , 'format': 'binary'}
                }
            }
        }
    )
    @action(detail=False , methods=["post"] , serializer_class = VehicleSerializer)
    def create_vehicle(self, request, *args, **kwargs):
        # serializer = 
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update Vehicle",
        operation_id= "update_vehicle",
        description= "captain or sub_admin or admin want to update vehicle",
        tags=["Vehicle"],
        request={
            'application/json':{
                'type': 'object',
                'properties' : {
                    "type":{'type':'string' , 'example':'light_truck' },
                    "accepted_volume":{'type':'double' , 'example': 1.5 },
                    "fuel_consumption_per_1km":{'type': "double" , 'example': "0.5" },
                    "fuel_type ":{'type': 'string' ,'example':"gasoline" },
                    "verified":{'type': 'boolean', 'example':True },
                    "delivery":{'type': 'boolean', 'example':False },
                    'image': {'type': 'string' , 'format': 'binary'}
                    # "captain":{'type': 'integer' , 'example': '1' }
                }
            }
        }
    )
    @action(detail=True , methods=["PATCH"] , serializer_class = VehicleSerializer)
    # TODO i have to fix the Bug
    def update_vehicle(self, request, *args, **kwargs):
        
        vehicle = Vehicle.objects.filter(id=kwargs.get("pk")).first()
        # credential = Credential. 
        re_captain = Captain.objects.filter(credentials=request.user.id).first()
        print(vehicle.captain.id)
        print(re_captain.id)
        print("///////////////////////////////////////////////////")
        if  (request.user.role == Credential.Role.CAPTAIN) and (vehicle.captain.id != re_captain.id):
            return Response({
                "detail":"you are not the vehicle captain"
            }, status.HTTP_400_BAD_REQUEST)
        
        if (vehicle.verified == True) and (request.user.role == Credential.Role.CAPTAIN):
            return Response({
                "detail":"the vehicle is verified so you can't change the details"
            }, status.HTTP_400_BAD_REQUEST)

        return super().partial_update(request, *args, **kwargs)

    
    @extend_schema(
        summary="List Vehicle",
        operation_id= "list_vehicle",
        description= "sub_admin or admin want to List vehicle",
        tags=["Vehicle"],
    )
    @action(detail=False , methods=["GET"] , serializer_class = VehicleSerializer)
    def list_vehicle(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class DiscountViewSet(ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [IsAdmin ]

    def get_permissions(self):
        if self.action == "list_trader_discount":
            self.permission_classes = [IsTrader]
        return super().get_permissions()

    @extend_schema(
        summary="Create Discount",
        operation_id= "create_discount",
        description= "admin want to create Discount",
        tags=["Discount"],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties' : {
                    "type":{'type':'string' ,'enum':['percent' , 'fixed' , 'full_free'] ,'example':'percent' },
                    "validation_datetime":{
                        "type": "string",
                        'format': 'custom-datetime',
                        'pattern': r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$',
                        "example":"2026-8-17 01:30"
                     },
                    "percent":{'type': "double" , 'example': "0.5" },
                    "fixed ":{'type': 'double' ,'example':"150" },
                }
            }
        }
    )
    def create(self, request, *args, **kwargs):
        type = request.data.get('type')
        fixed = request.data.get("fixed")
        percent = request.data.get("percent")
        print(fixed)
        print("//////////////////////////////////////")
        if type != "fixed" and fixed in [None , " "]:
            return Response({
                "detail":"you should change the type or make the fixed field null"},
                status=status.HTTP_400_BAD_REQUEST)
        if type == "full_free" and (fixed is not None or percent is not None):
            return Response({
                "detail":"its full free , you can't fill the percent or fixed field"}
                ,status = status.HTTP_400_BAD_REQUEST
            )
        if fixed not in [None , " "] and percent not in [None , " "]:
            return Response({
                "detail":"you can't fill the percent and fixed field to gather"}
                ,status = status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)


    @extend_schema(
        summary="Add Discount To Trader",
        operation_id= "add_discount_to_trader",
        description= "admin want to add discount to some trader",
        tags=["Discount"],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties' : {
                    "discount ":{'type': 'int' ,'example':1 },
                    "trader": {'type': 'array','items': {'type': 'integer'}}
                }
            }
        }
    )
    @action(detail=False , methods=['post'] , serializer_class=AddDiscountToTraderSerializer )
    def add_discount_to_trader(self , request , *args, **kwargs):
        # data = request.data.copy()
        data = dict(request.data.lists())
        print(data['trader'])
        if 'discount' in data and isinstance(data['discount'], list):
            data['discount'] = data['discount'][0] if data['discount'] else None
        # print(request.data)
        # print(f"Type of data['trader']: {type(data['trader'])}")
        # print(f"Value: {data['trader']}")
        # Convert dict like {"0": "1", "1": "2"} to list [1, 2]
        # if 'trader' in data and isinstance(data['trader'], dict):
        #     data['trader'] = [int(v) for v in data['trader'].values() if v]
        trader_ids = data.get('trader')
        if trader_ids is not None:
            # print("////////////////////////////")
            data['trader'] = self._parse_discount_trader_list(trader_ids)
        print(data)
        serializer = AddDiscountToTraderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # print("///////////////////////////////////////////////")

        discount_id = serializer.validated_data['discount']
        trader_ids = serializer.validated_data['trader']
        print(trader_ids)
        
        try:
            discount = Discount.objects.get(id=discount_id)
        except Discount.DoesNotExist:
            return Response({"detail": "Discount not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get valid traders only (ignore invalid IDs or raise error)
        traders = Trader.objects.filter(id__in=trader_ids)
        found_ids = set(traders.values_list('id', flat=True))
        missing = set(trader_ids) - found_ids

        if missing:
            return Response(
                {"detail": f"Traders with IDs {list(missing)} not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add the discount to each trader (assumes ManyToMany field)
        for trader in traders:
            trader.discounts.add(discount)  # change `discounts` to your actual related_name

        return Response(
            {"detail": f"Discount added to {len(traders)} trader(s)"},
            status=status.HTTP_200_OK
        )        

    def _parse_discount_trader_list(self, value):
        """Convert various input formats to a list of integers."""
        if isinstance(value, list):
            result = []
            for item in value:
                if isinstance(item, str) and ',' in item:
                    # Split comma-separated string (e.g., "2,3,1")
                    result.extend(int(x.strip()) for x in item.split(',') if x.strip())
                else:
                    result.append(int(item))
            return result

        elif isinstance(value, dict):
            # Handles "orders[0]=1&orders[1]=2"
            return [int(v) for v in value.values()]

        elif isinstance(value, str):
            # print("////////////////////////////")

            value = value.strip()
            if not value:
                return []
            if ',' in value:
                return [int(x.strip()) for x in value.split(',') if x.strip()]
            else:
                return [int(value)]

        else:
            # Fallback: let the serializer handle invalid types
            return []


    

    @extend_schema(
        summary="List Trader Discount",
        operation_id= "list_trader_discount",
        description= "admin want to List discount ",
        tags=["Discount"],
    )
    @action(detail=False , methods=["get"])
    def list_trader_discount(self, request, *args, **kwargs):
        queryset = Discount_Traders.objects.all()
        serializer = ListDiscountSerializer(queryset , many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # return super().list(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Discount",
        operation_id= "delete_discount",
        description= "admin want to Delete discount ",
        tags=["Discount"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        summary="Remove Discount on Trader",
        operation_id= "remove_discount_on_trader",
        description= "admin want to remove discount ",
        tags=["Discount"],
    )
    @action(detail=True , methods=['delete'] , serializer_class=ListDiscountSerializer)
    def remove_discount_on_trader(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        print(pk)
        discount_trader = Discount_Traders.objects.filter(pk=pk)
        if not discount_trader.exists():
            return Response({
                "detail": "The Trader Does't have Discount",
            } , status.HTTP_404_NOT_FOUND)
        discount_trader.delete()
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        summary="List Discount",
        operation_id= "list_discount",
        description= "admin want to List discount ",
        tags=["Discount"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    