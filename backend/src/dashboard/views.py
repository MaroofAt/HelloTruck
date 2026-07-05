from django.shortcuts import render

from rest_framework import viewsets ,status
from rest_framework.permissions import AllowAny

from tools.permissions import IsAdmin 

from drf_spectacular.utils import extend_schema

from .serializers import BranchSerializer , LocationSerializer

from .models import Branch , Location


class BranchViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    # permission_classes = [AllowAny]
    serializer_class = BranchSerializer
    queryset = Branch.objects.all()


    @extend_schema(
        summary="Create Branch",
        operation_id="create_branch",
        description="Admin can Create new Branch to the company",
        tags=['Branches'],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties': {
                    "title": {"type": 'string' , "example": 'Branch A'},
                    # "location": {
                    #     "type": "object",
                        
                    # }
                    "longitude": {"type": 'double' , "example" : '33.5104'},
                    "latitude": {"type": 'double' , "example" : '36.2783'}
                }
            }
        }  
    )
    def create (self , request , *args, **kwargs):
        # latitude = request.GET.get("latitude")
        # longitude = request.GET.get("longitude")

        # location , created = Location.objects.get_or_create(
        #         latitude=latitude, longitude=longitude, 
        #     )
        # request.add(location)
        serializer = self.get_serializer(data = request)
        if serializer.is_valid():
            serializer.save()
        return super().create(request, *args, **kwargs)


    @extend_schema(
        summary="List Branches",
        operation_id="list_branches",
        description="Getting All Branches",
        tags=["Branches"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    @extend_schema(
        summary="Retrieve Branches",
        operation_id="retrieve_branches",
        description="Getting specific Branch",
        tags=["Branches"],
    )
    def retrieve(self , request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    
    @extend_schema(
        summary="delete Branches",
        operation_id="delete_branches",
        description="delete specific Branch",
        tags=["Branches"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request , *args , **kwargs)


    @extend_schema(
        summary="Partial Update Branch",
        operation_id="partial_update_branch",
        description="Admin can update Branch ",
        tags=['Branches'],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties': {
                    "title": {"type": 'string' , "example": 'Branch A'},
                    # "location": {
                    #     "type": "object",
                        
                    # }
                    "longitude": {"type": 'double' , "example" : '33.5104'},
                    "latitude": {"type": 'double' , "example" : '36.2783'}
                }
            }
        } 
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    

# Create your views here.
class LocationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    @extend_schema(
        summary="Create Location",
        operation_id="create_location",
        description="Admin can Create new location to the company Branch",
        tags=['Locations'],
        request={
            'multipart/form-data':{
                'type': 'object',
                'properties': {
                    # "title": {"type": 'string' , "example": 'Branch A'},
                    # "location": {
                    #     "type": "object",
                        
                    # }
                    "longitude": {"type": 'double' , "example" : '33.5104'},
                    "latitude": {"type": 'double' , "example" : '36.2783'}
                }
            }
        }  
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
