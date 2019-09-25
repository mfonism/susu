from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from esusu import utils
from .models import (
    EsusuGroup,
    FutureTenure, LiveTenure, HistoricalTenure,
    Watch, LiveSubscription
)
from .serializers import (
    EsusuGroupSerializer,
    FutureTenureSerializer, LiveTenureSerializer, HistoricalTenureSerializer,
    WatchSerializer, LiveSubscriptionSerializer
)
from .permissions import IsGroupAdminOrReadOnly, IsGroupMember, IsOwner, IsGroupAdmin


class EsusuGroupViewSet(viewsets.ModelViewSet):
    queryset = EsusuGroup.objects.all()
    serializer_class = EsusuGroupSerializer
    permission_classes = [
        permissions.IsAuthenticated, IsGroupAdminOrReadOnly,
    ]

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)


    @action(methods=['post', 'put', 'delete'], detail=True,
            url_path='future-tenure', url_name='futuretenure')
    def future_tenure(self, request, pk=None):
        '''
        Write-actions for future tenures from their respective groups.
        '''
        group = self.get_object()

        if request.method == 'POST':
            # creating new future tenure
            serializer = FutureTenureSerializer(
                data=request.data,
                context={'request': request}
            )

            if not serializer.is_valid():
                return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

            try:
                ft = serializer.save(esusu_group=group)
            except IntegrityError:
                return utils.make_generic_400_response()

            # if all goes well, create watch on so created
            # future tenure for admin
            Watch.objects.create(tenure=ft, user=request.user)
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

        elif request.method == 'DELETE':
            # perform a hard delete on the object
            # so that we don't wrestle with integrity errors
            # when a new one is created for same group
            ft = get_object_or_404(FutureTenure, pk=group.hash_id)
            ft.delete(hard=True)
            return Response(status=status.HTTP_204_NO_CONTENT)


    @action(methods=['get'], detail=True,
            url_path='historical-tenure', url_name='historicaltenure',
            permission_classes=[permissions.IsAuthenticated, IsGroupMember])
    def historical_tenure(self, request, pk=None):
        '''
        List historical tenures from their respective groups.
        '''
        group = self.get_object()
        serializer = HistoricalTenureSerializer(
            HistoricalTenure.objects.filter(esusu_group=group),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(methods=['post', 'get'], detail=True,
            url_path='watch', url_name='watch',
            permission_classes=[permissions.IsAuthenticated])
    def watch(self, request, pk=None):
        '''
        Create and List actions for the watch model
        '''
        group = self.get_object()

        if request.method == 'POST':
            # Create a watch for the currently logged in user on (the
            # future tenure of) the esusu group identified by this view.
            try:
                watch = Watch.objects.create(
                    user=request.user, tenure=group.future_tenure
                )
            except (IntegrityError, ObjectDoesNotExist):
                return utils.make_generic_400_response()

            serializer = WatchSerializer(
                watch,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'GET':
            # List the watch objects on (the future tenure of) the esusu
            # group identified by this view if authenticated user is
            # the admin of the so identified group
            if not group.admin == request.user:
                return utils.make_generic_403_response()

            serializer = WatchSerializer(
                Watch.objects.filter(tenure__esusu_group=group),
                many=True,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)


    @action(methods=['get'], detail=True,
            url_path='live-subscription', url_name='livesubscription',
            permission_classes=[permissions.IsAuthenticated, IsGroupAdmin])
    def live_subscription(self, request, pk=None):
        '''
        List live subscriptions from their respective groups.
        '''
        group = self.get_object()

        serializer = LiveSubscriptionSerializer(
            LiveSubscription.objects.filter(tenure__esusu_group=group),
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class FutureTenureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FutureTenure.objects.all()
    serializer_class = FutureTenureSerializer


class LiveTenureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LiveTenure.objects.all()
    serializer_class = LiveTenureSerializer


class HistoricalTenureViewSet(mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet
                             ):
    queryset = HistoricalTenure.objects.all()
    serializer_class = HistoricalTenureSerializer


class WatchViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet
                  ):
    queryset = Watch.objects.all()
    serializer_class = WatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def perform_destroy(self, instance):
        instance.delete(hard=True)


class LiveSubscriptionViewSet(mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet
                              ):
    queryset = LiveSubscription.objects.all()
    serializer_class = LiveSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
