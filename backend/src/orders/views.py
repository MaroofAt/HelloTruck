from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action



from .models import Order
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
                    "special_shipment":{'type': 'integer', 'example':1 },
                    "longitude": {"type": 'double' , "example" : '36.2783'},
                    "latitude": {"type": 'double' , "example" : '33.5104'}
                }
            }
        }
    )
    def create (self, request, *args, **kwargs):
        
        if request.data.get("delivery") == True and request.data.get("shipment_type") not in ['FROM_BRANCH' , 'TO_BRANCH' , 'SPECIAL_SHIPMENT']:
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
        
        from_branch = Location.objects.get(id=request.data.get("from_branch"))
        if not from_branch:
            return Response(
                {"detail" : "this location not supported"} ,
                status=status.HTTP_404_NOT_FOUND
            )
        
        
        
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
            summary="Create delivery Order",
            operation_id= "create_delivery_order",
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
    
        
        


# Create your views here.
