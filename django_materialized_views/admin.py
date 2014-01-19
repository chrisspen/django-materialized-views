from django.conf import settings
from django.contrib import admin

import models

class MaterializedViewControlAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'app_label',
        'enabled',
        'stripable',
        'include_in_batch',
    )
    search_fields = (
        'name',
        'app_label',
    )
    list_filter = (
        'app_label',
        'enabled',
        'stripable',
        'include_in_batch',
    )
    readonly_fields = (
        'name',
        'app_label',
    )
    
    actions = (
        'enable',
        'disable',
    )
    
    def get_fieldsets(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        exclude = readonly_fields + ['id']
        fields = readonly_fields + [
            _.name for _ in self.model._meta.fields
            if _.name not in exclude
        ]
        fieldsets = (
            (None, {
                'fields': fields,
            }),
        )
        return fieldsets
    
    def enable(self, request, queryset):
        for r in queryset.iterator():
            r.enabled = True
            r.save()
    enable.short_description = 'Enable selected %(verbose_name_plural)s'
    
    def disable(self, request, queryset):
        for r in queryset.iterator():
            r.enabled = False
            r.save()
    disable.short_description = 'Disable selected %(verbose_name_plural)s'
    
admin.site.register(
    models.MaterializedViewControl,
    MaterializedViewControlAdmin)
