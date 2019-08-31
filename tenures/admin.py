from django.contrib import admin

from .models import (
    EsusuGroup, LiveTenure, HistoricalTenure, FutureTenure,
    LiveSubscription, HistoricalSubscription, Watch
    )


@admin.register(EsusuGroup)
class EsusuGroupAdmin(admin.ModelAdmin):
    empty_value_display = ''
    fields = (('name', 'get_hash_id'), ('admin', 'created_on'))
    list_display = ('get_hash_id', 'name', 'admin', 'created_on')
    list_display_links = ('get_hash_id',)
    readonly_fields = ('get_hash_id', 'created_on')
    ordering = ('-created_on', 'name')
    search_fields = ('name', 'admin')
    sortable_by = ('name', 'admin')

    def get_hash_id(self, instance):
        if instance.pk is None:
            return ''
        return instance.get_hash_id(instance.pk)

    get_hash_id.short_description = 'Hash ID'
