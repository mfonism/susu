from rest_framework import serializers

from .models import EsusuGroup


class EsusuGroupSerializer(serializers.HyperlinkedModelSerializer):

    admin_pk = serializers.ReadOnlyField(source='admin.pk')
    admin_firstname = serializers.ReadOnlyField(source='admin.firstname')
    admin_lastname = serializers.ReadOnlyField(source='admin.lastname')
    hash_id  = serializers.ReadOnlyField()

    class Meta:
        model = EsusuGroup
        fields = [
            'url', 'pk', 'name', 'hash_id',
            'admin_pk', 'admin_firstname', 'admin_lastname'
        ]
