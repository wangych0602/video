from rest_framework import serializers

from .models import ReviewLog, Video, VideoCategory, VideoSetting
from .models import VideoAlbum



def _default_cover_url(video):
    if video.cover_image:
        return video.cover_image.url
    setting = VideoSetting.objects.filter(pk=1).first()
    if setting and setting.default_cover:
        return setting.default_cover.url
    return None

class VideoCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoCategory
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class AlbumMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAlbum
        fields = ['id', 'name', 'cover_image']


class VideoSerializer(serializers.ModelSerializer):
    duration = serializers.DurationField(read_only=True)
    file_size = serializers.IntegerField(read_only=True)
    albums = AlbumMiniSerializer(many=True, read_only=True)
    album_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, required=False, source='albums', queryset=VideoAlbum.objects.all()
    )

    class Meta:
        model = Video
        fields = [
            'id',
            'title',
            'description',
            'teacher',
            'school',
            'category',
            'albums',
            'album_ids',
            'file',
            'cover_image',
            'duration',
            'file_size',
            'resolution',
            'status',
            'view_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'teacher', 'school', 'view_count', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get('cover_image'):
            data['cover_image'] = _default_cover_url(instance)
        return data


class VideoMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'cover_image', 'duration', 'status', 'file_size']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data.get('cover_image'):
            data['cover_image'] = _default_cover_url(instance)
        return data


class VideoAlbumSerializer(serializers.ModelSerializer):
    cover_image = serializers.ImageField(required=False)
    videos = VideoMiniSerializer(many=True, read_only=True)
    video_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, required=False, source='videos', queryset=Video.objects.all()
    )

    class Meta:
        model = VideoAlbum
        fields = [
            'id',
            'name',
            'teacher',
            'description',
            'cover_image',
            'view_count',
            'videos',
            'video_ids',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'teacher', 'view_count', 'created_at', 'updated_at']


class ReviewLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewLog
        fields = ['id', 'video', 'reviewer', 'action', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

class VideoSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSetting
        fields = ['id', 'banner_image', 'site_name', 'footer_description', 'footer_copyright', 'updated_at']
        read_only_fields = ['id', 'updated_at']
