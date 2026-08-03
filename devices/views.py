import datetime as dt
import secrets
import subprocess

from django.conf import settings
from django.utils import timezone
from urllib.parse import parse_qs
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from schools.models import School
from videos.models import Video

from .models import Device, LiveSession
from .permissions import IsAdminUser
from .serializers import DeviceSerializer, PublicLiveSessionSerializer

def _probe_duration(path):
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
        return None
    return None


def _get_device_from_request(request):
    device_sn = request.data.get('device_sn', '')
    token = request.headers.get('X-Device-Token', '')
    if not device_sn or not token:
        return None
    return Device.objects.filter(device_sn=device_sn, device_token=token).first()


def _device_or_admin_authed(request, device):
    user = getattr(request, 'user', None)
    if user and user.is_authenticated and (user.is_staff or user.role == 'admin'):
        return True
    if user and user.is_authenticated and user.role == 'teacher' and device.school_id == user.school_id:
        return True
    return request.headers.get('X-Device-Token', '') == device.device_token


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related('school').order_by('id')
    serializer_class = DeviceSerializer
    permission_classes = [IsAdminUser]
    search_fields = ['device_name', 'device_sn', 'school__name', 'ip_address', 'mac_address']

    @action(detail=False, methods=['get'], url_path='my-school', permission_classes=[AllowAny])
    def my_school(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response({'detail': '认证失败'}, status=401)
        if user.is_staff or user.role == 'admin':
            qs = self.get_queryset()
        elif user.role == 'teacher' and user.school_id:
            qs = Device.objects.select_related('school').filter(school_id=user.school_id).order_by('id')
        else:
            return Response({'detail': '没有权限'}, status=403)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        device_sn = request.data.get('device_sn', '').strip()
        device_name = request.data.get('device_name', '').strip()
        device_type = request.data.get('device_type', Device.DeviceType.RECORDING_HOST)
        manufacturer = request.data.get('manufacturer', '').strip()
        school_id = request.data.get('school')
        if not device_sn or not school_id:
            return Response({'detail': 'device_sn 和 school 为必填参数'}, status=400)
        school = School.objects.filter(id=school_id).first()
        if not school:
            return Response({'detail': '学校不存在'}, status=400)
        device, created = Device.objects.get_or_create(
            device_sn=device_sn,
            defaults={
                'device_name': device_name or device_sn,
                'device_type': device_type,
                'manufacturer': manufacturer,
                'school': school,
            },
        )
        if not created:
            device.device_name = device_name or device.device_name
            device.device_type = device_type
            device.manufacturer = manufacturer or device.manufacturer
            device.save(update_fields=['device_name', 'device_type', 'manufacturer', 'updated_at'])
        if not device.device_token:
            device.device_token = secrets.token_urlsafe(32)
            device.save(update_fields=['device_token', 'updated_at'])
        return Response(
            {'device_id': device.id, 'device_token': device.device_token},
            status=200 if not created else 201,
        )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def heartbeat(self, request):
        device = _get_device_from_request(request)
        if not device:
            return Response({'detail': '设备认证失败'}, status=401)
        device.status = Device.Status.ONLINE
        device.last_online_time = timezone.now()
        ip = request.data.get('ip_address') or request.META.get('REMOTE_ADDR')
        if ip:
            device.ip_address = ip
        device.save(update_fields=['status', 'last_online_time', 'ip_address', 'updated_at'])
        return Response(
            {
                'device_id': device.id,
                'status': device.status,
                'last_online_time': device.last_online_time,
            }
        )

    @action(detail=False, methods=['post'], url_path='upload-video', permission_classes=[AllowAny])
    def upload_video(self, request):
        device = _get_device_from_request(request)
        if not device:
            return Response({'detail': '设备认证失败'}, status=401)
        video_file = request.FILES.get('video_file')
        if not video_file:
            return Response({'detail': '请上传 video_file'}, status=400)
        record_time = request.data.get('record_time', '')
        title = request.data.get('title', '').strip()
        if not title:
            title = f'{device.device_name} 录像 {record_time or device.device_sn}'
        video = Video.objects.create(
            title=title,
            school=device.school,
            file=video_file,
            status=Video.Status.PENDING,
        )
        video.file_size = video.file.size or 0
        video.duration = _probe_duration(video.file.path) if video.file else None
        video.save(update_fields=['file_size', 'duration', 'updated_at'])
        return Response(
            {
                'id': video.id,
                'title': video.title,
                'status': video.status,
                'file_size': video.file_size,
                'school': video.school_id,
            },
            status=201,
        )

    @action(detail=True, methods=['post'], url_path='start-live', permission_classes=[AllowAny])
    def start_live(self, request, pk=None):
        device = self.get_object()
        if not _device_or_admin_authed(request, device):
            return Response({'detail': '设备认证失败'}, status=401)
        if device.status != Device.Status.ONLINE:
            return Response({'detail': '设备不在线，无法开始直播'}, status=400)
        now = timezone.now()
        stream_key = f'{device.device_sn}_{now:%Y%m%d}_{secrets.token_hex(4)}'
        rtmp_push_url = f'{settings.RTMP_SERVER_URL}/live/{stream_key}'
        hls_url = f'{settings.HLS_SERVER_URL}/hls/{stream_key}.m3u8'
        session = LiveSession.objects.create(
            device=device,
            title=request.data.get('title', '').strip() or f'{device.device_name} 直播',
            school=device.school,
            stream_key=stream_key,
            rtmp_push_url=rtmp_push_url,
            hls_url=hls_url,
            status=LiveSession.Status.STARTING,
        )
        device.status = Device.Status.STREAMING
        device.save(update_fields=['status', 'updated_at'])
        return Response(
            {
                'session_id': session.id,
                'stream_url': rtmp_push_url,
                'stream_key': stream_key,
                'hls_url': hls_url,
            }
        )

    @action(detail=True, methods=['post'], url_path='stop-live', permission_classes=[AllowAny])
    def stop_live(self, request, pk=None):
        device = self.get_object()
        if not _device_or_admin_authed(request, device):
            return Response({'detail': '设备认证失败'}, status=401)
        session = device.live_sessions.filter(
            status__in=[
                LiveSession.Status.CREATED,
                LiveSession.Status.STARTING,
                LiveSession.Status.LIVE,
            ]
        ).order_by('-id').first()
        if not session:
            return Response({'detail': '没有进行中的直播'}, status=400)
        session.status = LiveSession.Status.STOPPED
        session.end_time = timezone.now()
        session.save(update_fields=['status', 'end_time'])
        device.status = Device.Status.ONLINE
        device.save(update_fields=['status', 'updated_at'])
        return Response({'session_id': session.id, 'status': session.status})


class LiveSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LiveSession.objects.select_related('device', 'school').order_by('-created_time')
    serializer_class = PublicLiveSessionSerializer
    permission_classes = [AllowAny]
    search_fields = ['title', 'device__device_name', 'status']

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        mine = self.request.query_params.get('mine')
        if mine == '1' and self.request.user.is_authenticated:
            profile = getattr(self.request.user, 'teacher_profile', None)
            if profile:
                qs = qs.filter(teacher=profile)
            elif not (self.request.user.is_staff or getattr(self.request.user, 'role', '') == 'admin'):
                qs = qs.none()
        return qs


class LiveCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        raw_stream_key = request.data.get('stream_key') or request.data.get('name') or request.POST.get('name', '')
        raw_stream_key = str(raw_stream_key or '').strip()
        stream_key = raw_stream_key.split('?', 1)[0]
        event = request.data.get('event') or request.POST.get('call', '')
        event = str(event or '').strip()
        event_map = {
            'publish_started': LiveSession.Status.LIVE,
            'stream_started': LiveSession.Status.LIVE,
            'publish': LiveSession.Status.LIVE,
            'publish_stopped': LiveSession.Status.STOPPED,
            'stream_stopped': LiveSession.Status.STOPPED,
            'publish_done': LiveSession.Status.STOPPED,
            'stream_error': LiveSession.Status.ERROR,
        }
        if not stream_key or event not in event_map:
            return Response({'detail': 'stream_key 和 event 参数不合法'}, status=400)
        token = str(request.data.get('token') or request.POST.get('token') or request.query_params.get('token') or '').strip()
        if not token and '?' in raw_stream_key:
            token = parse_qs(raw_stream_key.split('?', 1)[1]).get('token', [''])[0]
        session = LiveSession.objects.select_related('device').filter(stream_key=stream_key).first()
        if not session:
            return Response({'detail': '直播会话不存在'}, status=404)
        now = timezone.now()
        target = event_map[event]
        if target == LiveSession.Status.LIVE:
            if session.token_used:
                return Response({'detail': '推流令牌已使用'}, status=403)
            if session.stream_token:
                if token and token != session.stream_token:
                    return Response({'detail': '推流令牌无效'}, status=403)
                session.stream_token = ''
                session.token_used = True
            session.status = target
            session.start_time = session.start_time or now
            session.save(update_fields=['status', 'start_time', 'stream_token', 'token_used'])
        elif target == LiveSession.Status.STOPPED:
            session.status = target
            session.end_time = now
            session.save(update_fields=['status', 'end_time'])
            if session.device_id:
                session.device.status = Device.Status.ONLINE
                session.device.save(update_fields=['status', 'updated_at'])
        else:
            session.status = target
            session.end_time = now
            session.save(update_fields=['status', 'end_time'])
            if session.device_id:
                session.device.status = Device.Status.ERROR
                session.device.save(update_fields=['status', 'updated_at'])
        return Response({'session_id': session.id, 'status': session.status})
