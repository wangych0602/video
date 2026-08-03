from django.contrib import admin

from .models import Building, School


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'building', 'created_at')
    list_filter = ('building',)
    search_fields = ('name', 'building__name')
