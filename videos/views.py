import datetime as dt
import subprocess
from django.db.models import F, Q
from rest_framework import viewsets
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ReviewLog, Video, VideoCategory, VideoSetting
from .models import VideoAlbum
from .permissions import IsAdminUser, IsPublicReadOrAdminOrOwner, IsPublicReadOrOwnerOrAdmin
from .serializers import ReviewLogSerializer, VideoAlbumSerializer, VideoCategorySerializer, VideoMiniSerializer, VideoSerializer, VideoSettingSerializer
from users.models import TeacherProfile
from users.serializers import TeacherDirectorySerializer


def _probe_duration(path):
    # 1. Try mutagen (pure Python, no external binary needed)
    try:
        from mutagen.mp4 import MP4
        from mutagen import File as MutagenFile

        media = MutagenFile(path)
        if media is not None and media.info is not None:
            length = getattr(media.info, 'length', None)
            if length and length > 0:
                return dt.timedelta(seconds=float(length))
    except Exception:
        pass

    # 2. Fallback: ffprobe (requires ffmpeg installed on system)
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-v',
                'error',
                '-show_entries',
                'format=duration',
                '-of',
                'default=noprint_wrappers=1:nokey=1',
                path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return dt.timedelta(seconds=float(result.stdout.strip()))
    except (FileNotFoundError, subprocess.SubprocessError, ValueError):
        pass
    return None

class VideoCategoryViewSet(viewsets.ModelViewSet):
    queryset = VideoCategory.objects.all()
    serializer_class = VideoCategorySerializer
    search_fields = ['name', 'description']


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.select_related('teacher__user', 'school', 'category').all()
    serializer_class = VideoSerializer
    permission_classes = [IsPublicReadOrAdminOrOwner]
    search_fields = ['title', 'description', 'school__name', 'category__name', 'teacher__user__username']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.role == 'admin'):
            qs = qs
        elif user.is_authenticated:
            qs = qs.filter(Q(teacher__user=user) | Q(status=Video.Status.PUBLISHED))
        else:
            qs = qs.filter(status=Video.Status.PUBLISHED)
        category_id = self.request.query_params.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_update(self, serializer):
        user = self.request.user
        if 'status' in serializer.validated_data and not (user.is_staff or user.role == 'admin'):
            serializer.validated_data.pop('status', None)
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        """访问视频详情时点击数 +1（使用 F 表达式避免并发竞争）"""
        instance = self.get_object()
        Video.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def popular(self, request):
        """返回点击量前 10 的已发布视频"""
        qs = Video.objects.filter(status=Video.Status.PUBLISHED).select_related(
            'teacher__user', 'school', 'category'
        ).order_by('-view_count', '-created_at')[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        user = request.user
        if not (user.is_staff or user.role == 'admin' or user.role == 'teacher'):
            return Response({'detail': '只有教师或管理员可以上传视频'}, status=403)
        if 'file' not in request.FILES:
            return Response({'detail': '请上传视频文件'}, status=400)
        teacher = getattr(user, 'teacher_profile', None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video = serializer.save(
            teacher=teacher,
            school=teacher.school if teacher else None,
            status=Video.Status.PENDING,
        )
        video.file_size = video.file.size or 0
        video.duration = _probe_duration(video.file.path) if video.file else None
        video.save(update_fields=['file_size', 'duration', 'updated_at'])
        return Response(self.get_serializer(video).data, status=201)

    @action(detail=False, methods=['get'])
    def my(self, request):
        qs = self.get_queryset().filter(teacher__user=request.user)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending(self, request):
        qs = Video.objects.filter(status=Video.Status.PENDING).select_related('teacher__user', 'school', 'category')
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        video = self.get_object()
        video.status = Video.Status.PUBLISHED
        video.save(update_fields=['status', 'updated_at'])
        ReviewLog.objects.create(
            video=video,
            reviewer=request.user,
            action=ReviewLog.Action.PUBLISHED,
            comment=request.data.get('comment', ''),
        )
        return Response(self.get_serializer(video).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        video = self.get_object()
        comment = request.data.get('comment', '').strip()
        if not comment:
            return Response({'detail': '拒绝时必须填写原因'}, status=400)
        video.status = Video.Status.REJECTED
        video.save(update_fields=['status', 'updated_at'])
        ReviewLog.objects.create(
            video=video,
            reviewer=request.user,
            action=ReviewLog.Action.REJECTED,
            comment=comment,
        )
        return Response(self.get_serializer(video).data)

class VideoAlbumViewSet(viewsets.ModelViewSet):
    queryset = VideoAlbum.objects.select_related('teacher__user', 'teacher__school').prefetch_related('videos').all()
    serializer_class = VideoAlbumSerializer
    permission_classes = [IsPublicReadOrOwnerOrAdmin]
    search_fields = ['name', 'description', 'teacher__user__username', 'teacher__school__name']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('mine') == '1' and self.request.user.is_authenticated:
            teacher = getattr(self.request.user, 'teacher_profile', None)
            if teacher:
                qs = qs.filter(teacher=teacher)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        teacher = getattr(user, 'teacher_profile', None)
        if not teacher:
            # 如果是管理员，自动创建教师资料
            if user.is_staff or user.role == 'admin':
                from schools.models import School
                school = School.objects.first()
                if not school:
                    from schools.models import Building
                    building = Building.objects.first() or Building.objects.create(name='默认教学楼')
                    school = School.objects.create(name='默认教室', building=building)
                teacher = TeacherProfile.objects.create(
                    user=user,
                    school=school,
                    subject='管理员',
                )
            else:
                raise PermissionDenied('只有教师才能创建专辑')
        serializer.save(teacher=teacher)

    def perform_update(self, serializer):
        serializer.save()

    def retrieve(self, request, *args, **kwargs):
        """访问专辑详情时点击数 +1"""
        instance = self.get_object()
        VideoAlbum.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def popular(self, request):
        """返回点击量前 10 的专辑"""
        qs = self.get_queryset().order_by('-view_count', '-created_at')[:10]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class StudioSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({'videos': [], 'albums': [], 'teachers': []})
        videos = Video.objects.filter(status=Video.Status.PUBLISHED).filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )[:8]
        albums = VideoAlbum.objects.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )[:8]
        teachers = TeacherProfile.objects.filter(
            Q(user__username__icontains=q) | Q(subject__icontains=q)
        )[:8]
        return Response({
            'videos': VideoMiniSerializer(videos, many=True).data,
            'albums': VideoAlbumSerializer(albums, many=True).data,
            'teachers': TeacherDirectorySerializer(teachers, many=True).data,
        })

class SiteSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        setting, _ = VideoSetting.objects.get_or_create(pk=1)
        return Response(VideoSettingSerializer(setting).data)
