from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ReviewLog, Video, VideoCategory, VideoSetting


@admin.action(description=_('批量审核通过并发布'))
def approve_selected(modeladmin, request, queryset):
    queryset.update(status=Video.Status.PUBLISHED)
    for video in queryset:
        ReviewLog.objects.create(
            video=video,
            reviewer=request.user,
            action=ReviewLog.Action.PUBLISHED,
            comment=_('后台批量审核通过'),
        )



@admin.action(description=_('批量拒绝'))
def reject_selected(modeladmin, request, queryset):
    queryset.update(status=Video.Status.REJECTED)
    for video in queryset:
        ReviewLog.objects.create(
            video=video,
            reviewer=request.user,
            action=ReviewLog.Action.REJECTED,
            comment=_('后台批量拒绝'),
        )


class ReviewLogInline(admin.TabularInline):
    model = ReviewLog
    extra = 0
    readonly_fields = ('action', 'comment', 'created_at')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'teacher', 'school', 'status', 'file_size', 'created_at')
    list_filter = ('status', 'category', 'school')
    search_fields = ('title', 'description', 'teacher__user__username', 'school__name')
    actions = [approve_selected, reject_selected]
    inlines = [ReviewLogInline]
    readonly_fields = ('file_size', 'created_at', 'updated_at')


@admin.register(VideoCategory)
class VideoCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ('video', 'reviewer', 'action', 'comment', 'created_at')
    list_filter = ('action',)
    search_fields = ('video__title', 'reviewer__username')
@admin.register(VideoSetting)
class VideoSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'site_name', 'banner_image', 'default_cover', 'updated_at')
