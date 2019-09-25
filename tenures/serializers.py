from django.utils import timezone
from rest_framework import serializers

from . import tasks
from .models import (
    EsusuGroup,
    FutureTenure, LiveTenure, HistoricalTenure,
    Watch, LiveSubscription
)


class EsusuGroupSerializer(serializers.HyperlinkedModelSerializer):

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


class FutureTenureSerializer(serializers.HyperlinkedModelSerializer):

    group = EsusuGroupSerializer(
        source='esusu_group',
        read_only=True
    )
    join_link = serializers.HyperlinkedRelatedField(
        source='esusu_group',
        read_only=True,
        view_name='esusugroup-watch'
    )

    class Meta:
        model = FutureTenure
        fields = [
            'url', 'amount', 'group', 'will_go_live_at', 'join_link'
        ]

    def create(self, validated_data):
        '''
        Ensure that there's enough time (at least 48 hours) to go live.
        '''
        if validated_data.get('will_go_live_at'):
            validated_data['will_go_live_at'] = max(
                validated_data['will_go_live_at'],
                timezone.now() + timezone.timedelta(2)
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        '''
        Watchers should review updates on this ft, and should be
        given enough time (at least 48 hours) to review the updates.
        '''
        tasks.reset_watches_on_updated_future_tenure(instance.pk)
        validated_data['will_go_live_at'] = max(
            validated_data.get('will_go_live_at', instance.will_go_live_at),
            timezone.now() + timezone.timedelta(2)
        )
        return super().update(instance, validated_data)


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

    class Meta:
        model = Watch
        fields = [
            'url', 'user_name', 'tenure_url', 'status'
        ]


class LiveSubscriptionSerializer(serializers.HyperlinkedModelSerializer):

    user_name = serializers.StringRelatedField(source='user')
    tenure_url = serializers.HyperlinkedRelatedField(
        source='tenure',
        read_only=True,
        view_name='livetenure-detail'
    )

    class Meta:
        model = LiveSubscription
        fields = [
            'url', 'user_name', 'tenure_url'
        ]
