from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from .models import (
    EsusuGroup, FutureTenure
)
from .serializers import (
    EsusuGroupSerializer, FutureTenureSerializer
)
from .permissions import IsGroupAdminOrReadOnly


class EsusuGroupViewSet(viewsets.ModelViewSet):
    queryset = EsusuGroup.objects.all()
    serializer_class = EsusuGroupSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsGroupAdminOrReadOnly,
    ]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

    @action(methods=['get', 'post'], detail=True,
            url_path='future-tenure', url_name='future-tenure')
    def future_tenure(self, request, pk=None):
        group = self.get_object()
        serializer = FutureTenureSerializer(
                        data=request.data,
                        context={'request': request}
        )

        if serializer.is_valid():
            serializer.save(esusu_group=group)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
