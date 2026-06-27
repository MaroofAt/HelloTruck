from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework import serializers

def exception_response(e):
    if isinstance(e, exceptions.ValidationError) or isinstance(e, serializers.ValidationError):
        return Response(
            data = str(e),
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {'Exception': str(e)},
        status=status.HTTP_409_CONFLICT
    )

def required_response(field_name):
    return Response(
        {'detail': f'{field_name} is required'},
        status=status.HTTP_400_BAD_REQUEST
    )
def method_not_allowed():
    return Response(
        {"detail": "Method not allowed"},
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )