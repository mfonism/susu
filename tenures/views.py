from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import EsusuGroup, FutureTenure
from .serializers import EsusuGroupSerializer, FutureTenureSerializer
from .permissions import IsGroupAdminOrReadOnly


class EsusuGroupViewSet(viewsets.ModelViewSet):
    queryset = EsusuGroup.objects.all()
    serializer_class = EsusuGroupSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsGroupAdminOrReadOnly,
    ]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)

    @action(methods=['post', 'put'], detail=True,
            url_path='future-tenure', url_name='future-tenure')
    def future_tenure(self, request, pk=None):
        '''
        Write-actions for future tenures from their respective groups.

        These actions are performed in the group view to solidify
        the following notion:
            + a group has one unique future tenure
            + a future tenure belongs to one unique group
            + a future tenure is created on a group

        This implementation also makes it easy to enforce that only
        the owner of a group can write to the group's future tenure.
        '''
        group = self.get_object()

        if request.method == 'POST':
            serializer = FutureTenureSerializer(
                data=request.data,
                context={'request': request}
            )

            if not serializer.is_valid():
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

            serializer.save(esusu_group=group)
            return Response(serializer.data, status.HTTP_200_OK)

        elif request.method == 'PUT':
            ft = get_object_or_404(FutureTenure, pk=group.hash_id)

            serializer = FutureTenureSerializer(
                instance=ft,
                data=request.data,
                context={'request': request}
            )

            if not serializer.is_valid():
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)

class FutureTenureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FutureTenure.objects.all()
    serializer_class = FutureTenureSerializer
