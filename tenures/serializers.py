from django.db.models import Value, QuerySet
from django.db.models.functions import Concat
from rest_framework import serializers

from .models import EsusuGroup


class EsusuGroupSerializer(serializers.HyperlinkedModelSerializer):

    admin_pk = serializers.ReadOnlyField(source='admin.pk')
    admin_fullname = serializers.ReadOnlyField()
    hash_id  = serializers.ReadOnlyField()

    class Meta:
        model = EsusuGroup
        fields = [
            'url', 'pk', 'name', 'hash_id', 'admin_pk', 'admin_fullname',
        ]

    def __new__(cls, *args, **kwargs):
        # this helps me create an annotation for fullname
        # on the queryset operated upon by this serializer
        if args and isinstance(args[0], QuerySet):
            queryset = cls._build_queryset(args[0])
            args = (queryset, ) + args[1:]
        return super().__new__(cls, *args, **kwargs)

    @classmethod
    def _build_queryset(cls, queryset):
        # just a helper I created
        # not in the official interface of serializers
        return queryset.annotate(
            admin_fullname=Concat(
                'admin__first_name',
                Value(' '),
                'admin__last_name'
            )
        )
