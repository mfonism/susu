from rest_framework import serializers

from .models import EsusuGroup


class EsusuGroupSerializer(serializers.HyperlinkedModelSerializer):

    admin_pk = serializers.ReadOnlyField(source='admin.pk')

    class Meta:
        model = EsusuGroup
        fields = ['url', 'pk', 'name', 'hash_id', 'admin_pk', 'admin']
