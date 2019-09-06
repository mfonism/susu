from rest_framework import viewsets
from rest_framework import permissions

from .models import EsusuGroup
from .serializers import EsusuGroupSerializer
from .permissions import IsGroupAdminOrReadOnly


class EsusuGroupViewSet(viewsets.ModelViewSet):
    queryset = EsusuGroup.objects.all()
    serializer_class = EsusuGroupSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsGroupAdminOrReadOnly,
    ]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)
