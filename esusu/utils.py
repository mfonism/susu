from rest_framework import status
from rest_framework.response import Response


def make_generic_400_response():
    '''
    Return generic response to bad request.
    '''
    return Response(
        {'error': 'Bad Request (400)'},
        status=status.HTTP_400_BAD_REQUEST
    )

def make_generic_403_response():
    '''
    Return generic response to request from entity without required permissions.
    '''
    return Response(
        {'error': 'You do not have permission to perform this action.'},
        status=status.HTTP_403_FORBIDDEN
    )
