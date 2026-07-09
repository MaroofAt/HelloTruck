from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action



from .models import Order , Order_Load , Trip
from .serializers import OrderSerializer

from tools.permissions import IsTrader

from dashboard.models import Location

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
                    "trader":{'type': 'integer' , 'example': '1' },
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
        
        # print(type(request.user.id), "//////////////////////////////////////")
        # print(type(request.data.get("trader")) ,"//////////////////////////////////////")
        if request.user.id != int(request.data.get("trader")):
            return Response(
                {"detail" : "You are note the Authenticated Trader"} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
        
        serializer = self.get_serializer(data=request.data)
        
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
                        "from_branch":{'type': 'integer', 'example':2 },
                        "longitude": {"type": 'double' , "example" : '36.2783'},
                        "latitude": {"type": 'double' , "example" : '33.5104'},

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
                'from_branch': request.data.get("from_branch"), #Changeee
                'special_shipment': order.special_shipment.id if order.special_shipment else None,
                'longitude': request.data.get("longitude"),
                'latitude': request.data.get("latitude")
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
                    "goods_type":{'type': "string" ,'enum': ['liquid', 'need_refrigeration', 'normal_Breakable', 'normal'], 'example':'normal' },
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
        
        if request.data.get("delivery") == False and (request.data.get("from_branch") == None or request.data.get("to_branch") ==  None) :
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
    

    
        
        


# Create your views here.
