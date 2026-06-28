from django.shortcuts import render

from rest_framework import viewsets ,status

from tools.permissions import IsAdmin 

from drf_spectacular.utils import extend_schema

from .serializer import BranchSerializer


class BranchViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = BranchSerializer



    @extend_schema(
        summary="Create Branch",
        operation_id="create_branch",
        description="Admin can Create new Branch to the company",
        tags=['Branches'],
        request={
            'multipart/from-data':{
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
            'multipart/from-data':{
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
