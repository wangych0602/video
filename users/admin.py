from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import TeacherProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'school', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (('平台信息', {'fields': ('role', 'school')}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (('平台信息', {'fields': ('role', 'school')}),)


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'subject')
    search_fields = ('user__username', 'school__name', 'subject')
