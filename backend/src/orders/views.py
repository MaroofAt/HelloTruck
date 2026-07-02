from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status


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
                    "goods_type":{'type': "string" ,'enum': ['LIQUID', 'NEED_REFRIGERATION', 'NORMAL_BREAKABLE', 'NORMAL'], 'example':'NORMAL' },
                    # "price":{'type':"double" , 'example':2200 },
                    "distance":{'type':"string" , 'example': "100km"},
                    "delivery":{'type': "boolean" , 'example': "True" },
                    "shipment_type":{'type':"string" ,'enum': ['LTL' , 'EUV' , 'SPECIAL_SHIPMENT' , 'FROM_BRANCH' , 'TO_BRANCH' , 'ecommerce_delivery'], 'example': 'LTL'},
                    "trader":{'type': 'integer' , 'example': '1' },
                    "destination":{'type':'integer' , 'example':1 },
                    "from_branch":{'type': 'integer', 'example':1 },
                    "special_shipment":{'type': 'integer', 'example':1 },
                }
            }
        }
    )
    def create (self, request, *args, **kwargs):
        
        if request.get("delivery") == True & request.get("shipment_type") not in ['FROM_BRANCH' , 'TO_BRANCH' , 'SPECIAL_SHIPMENT']:
            return Response(
                {"detail" : "the delivery flag should be False"} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.get("delivery") == False & request.get("shipment_type") not in ['EUV' , 'LTL' , 'SPECIAL_SHIPMENT']:
            return Response(
                {"detail" : "the delivery flag should be True"} ,
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.id != request.get("trader"):
            return Response(
                {"detail" : "You are note the Authenticated Trader"} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        destination = Location.objects.get(id=request.get("destination"))
        if not destination:
            return Response(
                {"detail" : "this location not supported"} ,
                status=status.HTTP_404_NOT_FOUND
            )
        
        from_branch = Location.objects.get(id=request.get("from_branch"))
        if not from_branch:
            return Response(
                {"detail" : "this location not supported"} ,
                status=status.HTTP_404_NOT_FOUND
            )
        
        if from_branch.id == destination.id:
            return Response(
                {"detail" : "You Order from/to the same branch "} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.get("special_shipment") == True & request.get("shipment_type") != 'SPECIAL_SHIPMENT' :
            return Response(
                {"detail" : "it is a special shipment  "} ,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request)
        
        if serializer.is_valid():
            serializer.save()
         
            return Response({
                'data': serializer.data,
                'result': ""#result
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'errors': serializer.errors,
            'result': ""#result
        }, status=status.HTTP_400_BAD_REQUEST)
        
        

# Create your views here.
