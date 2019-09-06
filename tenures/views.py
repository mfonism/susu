from rest_framework import viewsets

from .models import EsusuGroup
from .serializers import EsusuGroupSerializer


class EsusuGroupViewSet(viewsets.ModelViewSet):
    queryset = EsusuGroup.objects.all()
    serializer_class = EsusuGroupSerializer

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)
