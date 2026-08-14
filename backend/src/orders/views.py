from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from users.models import Credential  

from .models import Order , Order_Load , Trip 
from .serializers import OrderSerializer , TripSerializer

from tools.permissions import IsTrader , IsAdmin , IsSubAdmin , IsCaptain 

from dashboard.models import Location

from users.models import Trader

from drf_spectacular.utils import extend_schema




class OrderViewSet (viewsets.ModelViewSet):
    permission_classes = [IsTrader]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    @extend_schema(
        summary="Create Order",
        operation_id= "create_order",
        description= "Trader want to create order on the application",
        tags=["Order"],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties' : {
                    "volume":{'type':'double' , 'example':44.65 },
                    "weight":{'type':'double' , 'example': 15.5 },
                    "goods_type":{'type': "string" ,'enum': ['liquid', 'need_refrigeration', 'normal_Breakable', 'normal'], 'example':'normal' },
                    # "price":{'type':"double" , 'example':2200 },
                    # "distance":{'type':"string" , 'example': "100km"},
                    "delivery":{'type': "boolean" , 'example': "True" },
                    "shipment_type":{'type':"string" ,'enum': ['LTL' , 'EUV' , 'SPECIAL_SHIPMENT' , 'FROM_BRANCH' , 'TO_BRANCH' , 'ecommerce_delivery'], 'example': 'LTL'},
                    # "trader":{'type': 'integer' , 'example': '1' },
                    # "destination":{'type':'integer' , 'example':1 },
                    "from_branch":{'type': 'integer', 'example':2 },
                    "to_branch":{'type': 'integer', 'example':3 },
                    "special_shipment":{'type': 'integer', 'example':1 },
                    # "longitude": {"type": 'double' , "example" : '36.2783'},
                    # "latitude": {"type": 'double' , "example" : '33.5104'}

                    "longitude_from": {"type": 'double' , "example" : '36.2783'},
                    "latitude_from": {"type": 'double' , "example" : '33.5104'},
                    "longitude_to": {"type": 'double' , "example" : '37.2783'},
                    "latitude_to": {"type": 'double' , "example" : '34.5104'}
                }
            }
        }
    )
    def create (self, request, *args, **kwargs):
        print(request.data)
        
        if request.data.get("delivery") == True and request.data.get("shipment_type") not in ['FROM_BRANCH' , 'TO_BRANCH' , 'ecommerce_delivery' , 'SPECIAL_SHIPMENT']:
            return Response(
                {"detail" : "the delivery flag should be False"} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.data.get("delivery") == False and request.data.get("shipment_type") not in ['EUV' , 'LTL' , 'SPECIAL_SHIPMENT']:
            return Response(
                {"detail" : "the delivery flag should be True"} ,
                status=status.HTTP_400_BAD_REQUEST
            )

        trader = Trader.objects.filter(credentials_id=request.user.id)
        trader = trader.first()
        data = request.data.copy()
        data['trader'] = trader.id
        # print(request.user.id, "//////////////////////////////////////")
        # print(request.data.get("trader") ,"//////////////////////////////////////")
        # if request.user.id != int(request.data.get("trader")):
        #     return Response(
        #         {"detail" : "You are note the Authenticated Trader"} ,
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        # destination = Location.objects.get(id=request.data.get("destination"))
        # if not destination:
        #     return Response(
        #         {"detail" : "this location not supported"} ,
        #         status=status.HTTP_404_NOT_FOUND
        #     )
        
        # from_branch = Location.objects.get(id=request.data.get("from_branch"))
        # if not from_branch:
        #     return Response(
        #         {"detail" : "this location not supported"} ,
        #         status=status.HTTP_404_NOT_FOUND
        #     )

        # if
        
        
        
        if request.data.get("special_shipment") == True and request.data.get("shipment_type") != 'SPECIAL_SHIPMENT' :
            return Response(
                {"detail" : "it is a special shipment  "} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=data)
        
        if serializer.is_valid():
            serializer.save()

            return Response({
                'data': serializer.data,
                'result': ""#result
            }, status=status.HTTP_201_CREATED)
        print(serializer.errors , "//////////////////////////////////////////////////")
        return Response({
            'errors': serializer.errors,
            'result': ""#result
        }, status=status.HTTP_400_BAD_REQUEST)
        
        

    @extend_schema(
            summary="Create delivery Order After Shipment",
            operation_id= "create_delivery_after_shipment",
            description= "Trader want to create delivery order to the same delivery shipment on the application",
            tags=["Order"],
            request={
                'multipart/form-data':{
                    'type': 'object',
                    'properties' : {
                        "order":{'type': 'integer', 'example':1 },
                        # "from_branch":{'type': 'integer', 'example':2 },
                        "longitude_to": {"type": 'double' , "example" : '36.2783'},
                        "latitude_to": {"type": 'double' , "example" : '33.5104'},

                    }
                }
            }
    )
    @action(detail=False , methods=['post'] , serializer_class=OrderSerializer)
    def create_delivery_after_shipment(self, request, *args, **kwargs):
        if not request.data.get("order"):
            return Response({
                'detail': "Order ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.get(id=request.data.get("order"))
        if order:
            if order.delivery == True:
                return Response({
                    'detail': "Order already delivered"
                } , status=status.HTTP_400_BAD_REQUEST)
            # order.delivery = True

            

            new_order_data = {
                'volume': order.volume,
                'weight': order.weight,
                'goods_type': order.goods_type,
                'delivery': True,  
                'shipment_type': order.shipment_type,
                'trader': order.trader.id,
                # 'destination': order.destination.id, #changeeee
                'from_branch': order.from_branch.id,
                'to_branch' : None,
                'special_shipment': order.special_shipment.id if order.special_shipment else None,
                'longitude_to': request.data.get("longitude_to"),
                'latitude_to': request.data.get("latitude_to"),
                'longitude_from': None,
                'latitude_from': None,

            }

            serializer = self.get_serializer(data=new_order_data)

            if serializer.is_valid():
                serializer.save()

                return Response({
                    'data': serializer.data,
                    'result': ""#result
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'errors': serializer.errors,
                'result': ""
            } , status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'detail': "Order Does't Exist"
        } , status=status.HTTP_404_NOT_FOUND)
    



    @extend_schema(
        summary="Update Order",
        operation_id= "update_order",
        description= "Trader want to update order on the application",
        tags=["Order"],
        request={
            'application/json':{
                'type': 'object',
                'properties' : {
                    "volume":{'type':'double' , 'example':44.65 },
                    "weight":{'type':'double' , 'example': 15.5 },
                    "goods_type":{'type': "string" ,'enum': ['liquid', 'need_refrigeration', 'normal_breakable', 'normal'], 'example':'normal' },
                    "delivery":{'type': "boolean" , 'example': "True" },
                    "shipment_type":{'type':"string" ,'enum': ['LTL' , 'EUV' , 'SPECIAL_SHIPMENT' , 'FROM_BRANCH' , 'TO_BRANCH' , 'ecommerce_delivery'], 'example': 'LTL'},
                    "trader":{'type': 'integer' , 'example': '1' },
                    "from_branch":{'type': 'integer', 'example':2 },
                    "to_branch":{'type': 'integer', 'example':3 },
                    "special_shipment":{'type': 'integer', 'example':1 },
                    "longitude_from": {"type": 'double' , "example" : '36.2783'},
                    "latitude_from": {"type": 'double' , "example" : '33.5104'},
                    "longitude_to": {"type": 'double' , "example" : '37.2783'},
                    "latitude_to": {"type": 'double' , "example" : '34.5104'}
                }
            }
        }
    )
    def partial_update(self, request, *args, **kwargs):

        print(request.data)

        if request.data.get("delivery") == True and request.data.get("shipment_type") not in ['FROM_BRANCH' , 'TO_BRANCH' , 'ecommerce_delivery' , 'SPECIAL_SHIPMENT']:
            return Response(
                {"detail" : "the delivery flag should be False"} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.data.get("delivery") == False and request.data.get("shipment_type") not in ['EUV' , 'LTL' , 'SPECIAL_SHIPMENT']:
            return Response(
                {"detail" : "the delivery flag should be True"} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # from_branch = Location.objects.get(id=request.data.get("from_branch"))
        # if not from_branch:
        #     return Response(
        #         {"detail" : "this location not supported"} ,
        #         status=status.HTTP_404_NOT_FOUND
        #     )
        
        if request.data.get("delivery") == False and (request.data.get("from_branch") == None and request.data.get("to_branch") ==  None) :
            return Response(
                {"detail" : "You should select the from/to our branches not the location"} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.data.get("delivery") == True and (request.data.get("from_location") == None and request.data.get("to_location") == None):
            return Response(
                {"detail" : "You should select the (from|to) location "} ,
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.data.get("special_shipment") == True and request.data.get("shipment_type") != 'SPECIAL_SHIPMENT' :
            return Response(
                {"detail" : "it is a special shipment  "} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        pk = kwargs.get("pk")
        order = Order.objects.filter(id=pk)
        if not order.exists():
            return Response(
                {"detail": "order does't exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        order = order.first()

        serializer = self.get_serializer(
            instance = order,
            data = {**request.data}
        )

        if serializer.is_valid():
            # serializer.save()
            self.partial_update(serializer)

            return Response({
                'data': serializer.data,
                'result': ""#result
            }, status=status.HTTP_202_ACCEPTED)

        # print(serializer.errors,"//////////////////////////////////////////////////////////")
        return Response({
            'errors': serializer.errors,
            'result': ""#result
        }, status=status.HTTP_400_BAD_REQUEST)
        
        # return super().update(request, *args, **kwargs)



    @extend_schema(
            summary="Cancel Order",
            operation_id= "cancel_order",
            description= "Trader want to cancel the order before launch status or before the admin add it to trip on the application",
            tags=["Order"],
            # request={
            #     'multipart/form-data':{
            #         'type': 'object',
            #         'properties' : {
            #             "order":{'type': 'integer', 'example':1 },
            #         }
            #     }
            # }
    )
    @action(detail=True , methods=['delete'] , serializer_class=OrderSerializer)
    def cancel_order(self, *args, **kwargs):
        order_id = kwargs.get("pk")
        order = Order.objects.filter(pk = order_id)
        if not order:
            return Response(
                {"detail": "Order not created yet"},
                status=status.HTTP_404_NOT_FOUND
            )
        order = order.first()
        order_load = Order_Load.objects.filter(order=order)
        if order_load:
            trip = Trip.objects.filter(id=order_load.trip)
            if trip.status not in ["PENDING","pending", "Pending"]:
                return Response(
                    {"detail" : "you can't cancel the order it is't in pending status "},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        order.delete()
        return Response({"detail": "Order has been canceled and deleted "}, status=status.HTTP_200_OK)
    
    

    
        
class TripViewSet (viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated ]
    serializer_class = TripSerializer
    queryset = Trip.objects.all()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated ]
        if  self.action == "create_trip" or self.action == "create_EUV_trip":
            if self.request.user.is_authenticated and self.request.user.role != Credential.Role.ADMIN:
                self.permission_classes.append(IsSubAdmin) 
        if self.action == "change_status":
            if self.request.user.is_authenticated and self.request.user.role != Credential.Role.ADMIN:
                    if self.request.user.role != Credential.Role.SUB_ADMIN:
                        self.permission_classes.append(IsCaptain) 
                    else:   
                        self.permission_classes.append(IsSubAdmin) 
        if self.action == "change_status_to_complete":
            if self.request.user.is_authenticated and self.request.user.role != Credential.Role.ADMIN:
                    if self.request.user.role != Credential.Role.SUB_ADMIN:
                        self.permission_classes.append(IsTrader)
                    else:
                        self.permission_classes.append(IsSubAdmin)

        if self.action == "load_trip_manually":
            if self.request.user.is_authenticated and self.request.user.role != Credential.Role.ADMIN:
                self.permission_classes.append(IsSubAdmin) 



            # self.permission_classes.append(IsSubAdmin) 
            # self.permission_classes.append(IsAdmin) 
            # return [IsAuthenticated, (IsSubAdmin | IsAdmin)]


        return super().get_permissions()

    @extend_schema(
        summary="Create Trip",
        operation_id= "create_trip",
        description= "sup_admin or admin want to create Trip has many order",
        tags=["Trips"],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties' : {
                    "launch_datetime" : {
                        "type": "string",
                        'format': 'custom-datetime',
                        'pattern': r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$',
                        "example":"2026-8-16 10:30"
                        },
                    "arrival_datetime":{
                        "type": "string",
                        'format': 'custom-datetime',
                        'pattern': r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$',
                        "example":"2026-8-20 05:30"
                    },
                }
            }
        }
    )
    @action(detail=False , methods=["post"] , serializer_class=TripSerializer )
    def create_trip(self, request, *args, **kwargs):
        data = request.data.copy()
        data.update( {
            "status":"pending"
        })
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
        
            return Response({
                'data': serializer.data,
                'result': ""#result
                }, status=status.HTTP_201_CREATED
            )
        
        return Response({
            'errors': serializer.errors,
            'result': ""#result
            }, status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary="Change Status",
        operation_id= "change_status",
        description= "captain or sup_admin or admin want to change trip status ",
        tags=["Trips"],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties': {
                    "status": {'type':"string" ,
                            'enum': ["pending" , "launched" , "delivered" ] ,
                            "example": 'launched'
                    },
                }
            }
        } 
    )
    @action(detail=True , methods=['patch'] , serializer_class = TripSerializer)
    def change_status(self, request, *args, **kwargs):
        trip_id = kwargs.get("pk")
        trip = Trip.objects.filter(id=trip_id)
        if not trip.exists():
            return Response({"detail": "Trip Doesn't Exists"} , status=status.HTTP_404_NOT_FOUND)

        trip = trip.first()

        if not request.data.get("status") :
            return Response({"detail": "status is requierd"} , status=status.HTTP_400_BAD_REQUEST)
            

        trip.status = request.data.get("status")
        # trip.save()
        serializer = self.get_serializer(instance=trip, data=request.data , partial=True)
        if serializer.is_valid():
            print("//////////////////////////////////////////////////////////////////")
            serializer.save()
        
            return Response({
                'data': serializer.data,
                'result': ""#result
                }, status=status.HTTP_201_CREATED)

        return Response({
                    'errors': serializer.errors,
                    'result': ""#result
                    }, status=status.HTTP_400_BAD_REQUEST
                )

    
    @extend_schema(
        summary="Create EUV Trip",
        operation_id= "create_EUV_trip",
        description= "sup_admin or admin want to create Trip has many order",
        tags=["Trips"],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties' : {
                    "launch_datetime" : {
                        "type": "string",
                        'format': 'custom-datetime',
                        'pattern': r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$',
                        "example":"2026-8-16 10:30"
                        },
                    "arrival_datetime":{
                        "type": "string",
                        'format': 'custom-datetime',
                        'pattern': r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$',
                        "example":"2026-8-20 05:30"
                    },
                    "order_id":{ "type": "int", "example": 1 },
                    "vehicle_id" : {"type" : "int" , "example": 1},
                }
            }
        }
    )
    @action(detail=False , methods=["post"] , serializer_class=TripSerializer )
    def create_EUV_trip(self, request, *args, **kwargs):
        if not request.date.get("vehicle_id"):
            return Response({'detail':'vehicle_id is requierd'} , status = status.HTTP_400_BAD_REQUEST)

        if not request.date.get("order_id"):
            return Response({'detail':'order_id is requierd'} , status = status.HTTP_400_BAD_REQUEST)
        
        new_data = {
            "launch_datetime": request.date.get("launch_datetime"),
            "arrival_datetime": request.date.get("arrival_datetime"),
            "status":"pending",
        } 
        serializer = TripSerializer(data = new_data)

        if serializer.is_valid():
            serializer.save()
            order_load = Order_Load.objects.create({
                "trip": request.data.get("id"),
                "order": request.data.get("order"),
                "vehicle": request.data.get("vehicle"),
                "load_percent": 100,
            })
            order_load.save()
            out_data = {
                serializer.data,
                order_load
            }
            if order_load:
                return Response({"data":out_data}, status.HTTP_201_CREATED)
            
        return Response({
            'errors': serializer.errors,
            'result': ""#result
            }, status=status.HTTP_400_BAD_REQUEST
        )


    @extend_schema(
        summary="Change Status to Complete",
        operation_id= "change_status_to_complete",
        description= "trader or sup_admin or admin want to change trip status ",
        tags=["Trips"],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties': {
                    "status": {'type':"string" ,
                            'enum': ["complete" , "complete_with_damage"] ,
                            "example": 'complete'
                    },
                }
            }
        } 
    )
    @action(detail=True , methods=['patch'] , serializer_class = TripSerializer)
    def change_status_to_complete(self, request, *args, **kwargs):
        trip_id = kwargs.get("pk")
        trip = Trip.objects.filter(id=trip_id)
        if not trip.exists():
            return Response({"detail": "Trip Doesn't Exists"} , status=status.HTTP_404_NOT_FOUND)

        trip = trip.first()

        if not request.data.get("status") :
            return Response({"detail": "status is requierd"} , status=status.HTTP_400_BAD_REQUEST)
            

        trip.status = request.data.get("status")
        # trip.save()
        serializer = self.get_serializer(instance=trip, data=request.data , partial=True)
        if serializer.is_valid():
            print("//////////////////////////////////////////////////////////////////")
            serializer.save()
        
            return Response({
                'data': serializer.data,
                'result': ""#result
                }, status=status.HTTP_201_CREATED)

        return Response({
            'errors': serializer.errors,
            'result': ""#result
            }, status=status.HTTP_400_BAD_REQUEST
        )
# TODO///////////////////
    @extend_schema(
        summary="Load Trip Manually",
        operation_id= "load_trip_manually",
        description= "sup_admin or admin want to load the trip manually ",
        tags=["Trips"],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties': {
                    "orders": {'type': 'array','items': {'type': 'integer'},'description': 'List of order IDs to assign to this trip'},
                    "trip": {'type':'int' , 'example':1},
                    'vehicle':{'type':'int' , 'example':1},
                }
            }
        } 
    )
    @action(detail=False , methods=['post'] , serializer_class=TripSerializer)
    def load_trip_manually(self,request , *args, **kwargs):
        orders_ids = request.data.get("orders" , [])
        if isinstance(orders_ids, str):
            orders_ids = [int(id.strip()) for id in orders_ids.split(',')]
        elif isinstance(orders_ids, list):
            orders_ids = [int(id) for id in orders_ids]
        # print(orders_ids[0])
        
        return Response({} , status.HTTP_200_OK)






# Create your views here.
