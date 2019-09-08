from rest_framework import viewsets, mixins

from .models import User
from .serializers import UserSerializer


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet
                  ):
    serializer_class = UserSerializer
    queryset = User.objects.all()
