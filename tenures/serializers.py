# from django.db.models import Value, QuerySet
# from django.db.models.functions import Concat
from rest_framework import serializers

from .models import (
    EsusuGroup,
    FutureTenure, LiveTenure, HistoricalTenure,
    Watch,
)


class EsusuGroupSerializer(serializers.HyperlinkedModelSerializer):

    # admin_name = serializers.ReadOnlyField()
    admin_name = serializers.StringRelatedField(source='admin')
    admin_url = serializers.HyperlinkedRelatedField(
        source='admin',
        read_only=True,
        view_name='user-detail'
    )
    hash_id  = serializers.ReadOnlyField()

    class Meta:
        model = EsusuGroup
        fields = [
            'url', 'name', 'hash_id', 'admin_name', 'admin_url'
        ]

    # def __new__(cls, *args, **kwargs):
    #     # this helps me create an annotation for fullname
    #     # on the queryset operated upon by this serializer
    #     if args and isinstance(args[0], QuerySet):
    #         queryset = cls._build_queryset(args[0])
    #         args = (queryset, ) + args[1:]
    #     return super().__new__(cls, *args, **kwargs)

    # @classmethod
    # def _build_queryset(cls, queryset):
    #     # just a helper I created
    #     # not in the official interface of serializers
    #     return queryset.annotate(
    #         admin_name=Concat(
    #             'admin__first_name',
    #             Value(' '),
    #             'admin__last_name'
    #         )
    #     )


class FutureTenureSerializer(serializers.HyperlinkedModelSerializer):

    group = EsusuGroupSerializer(
        source='esusu_group',
        read_only=True
    )
    join_link = serializers.CharField(
        # for now, let it just be the hash_id
        source='esusu_group.hash_id',
        read_only=True
    )

    class Meta:
        model = FutureTenure
        fields = [
            'url', 'amount', 'group', 'will_go_live_at', 'join_link'
        ]


class LiveTenureSerializer(serializers.HyperlinkedModelSerializer):

    group = EsusuGroupSerializer(
        source='esusu_group',
        read_only=True
    )

    class Meta:
        model = LiveTenure
        fields = [
            'url', 'amount', 'group', 'live_at'
        ]


class HistoricalTenureSerializer(serializers.HyperlinkedModelSerializer):

    group = EsusuGroupSerializer(
        source='esusu_group',
        read_only=True
    )
    dissolved_at = serializers.ReadOnlyField(source='created_at')

    class Meta:
        model = HistoricalTenure
        fields = [
            'url', 'amount', 'group', 'dissolved_at'
        ]


class WatchSerializer(serializers.HyperlinkedModelSerializer):

    user_name = serializers.StringRelatedField(source='user')
    tenure_url = serializers.HyperlinkedRelatedField(
        source='tenure',
        read_only=True,
        view_name='futuretenure-detail'
    )
    opt_in = serializers.BooleanField(required=False, source='has_opted_in')

    class Meta:
        model = Watch
        fields = [
            'url', 'user_name', 'tenure_url', 'opt_in',
        ]
