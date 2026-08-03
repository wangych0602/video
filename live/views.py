from rest_framework import viewsets

from .models import LiveRoom
from .serializers import LiveRoomSerializer


class LiveRoomViewSet(viewsets.ModelViewSet):
    queryset = LiveRoom.objects.select_related('school', 'teacher').order_by('id')
    serializer_class = LiveRoomSerializer
    search_fields = ['name', 'school__name', 'status']


import secrets

from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from devices.models import Device, LiveSession


class PersonalLiveStartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not (user.is_staff or user.role in ('admin', 'teacher')):
            return Response({'detail': '没有权限'}, status=403)
        profile = getattr(user, 'teacher_profile', None)
        teacher = profile if (profile and profile.school_id) else None
        school = teacher.school if teacher else (user.school if user.school_id else None)
        now = timezone.now()
        token = secrets.token_hex(6)
        stream_key = f'teacher_{user.id}_{now:%Y%m%d}_{token}'
        display = teacher.user.username if teacher else user.username
        title = str(request.data.get('title', '')).strip() or f'{display} 的个人直播'
        rtmp_push_url = f'{settings.RTMP_SERVER_URL}/live/{stream_key}'
        hls_url = f'{settings.HLS_SERVER_URL}/hls/{stream_key}.m3u8'
        session = LiveSession.objects.create(
            device=None,
            teacher=teacher,
            school=school,
            title=title,
            stream_key=stream_key,
            stream_token=token,
            rtmp_push_url=rtmp_push_url,
            hls_url=hls_url,
            status=LiveSession.Status.CREATED,
        )
        return Response(
            {
                'session_id': session.id,
                'title': session.title,
                'stream_url': rtmp_push_url,
                'stream_key': stream_key,
                'push_token': token,
                'hls_url': hls_url,
            },
            status=201,
        )

def _can_manage_live(user, session):
    if user.is_staff or getattr(user, 'role', '') == 'admin':
        return True
    profile = getattr(user, 'teacher_profile', None)
    if profile and session.teacher_id == profile.id:
        return True
    return getattr(user, 'role', '') == 'school_admin' and user.school_id and session.school_id == user.school_id


class PersonalLiveStopView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        session = LiveSession.objects.filter(pk=session_id).first()
        if not session:
            return Response({'detail': '直播不存在'}, status=404)
        if not _can_manage_live(request.user, session):
            return Response({'detail': '没有权限'}, status=403)
        if session.status not in (
            LiveSession.Status.CREATED,
            LiveSession.Status.STARTING,
            LiveSession.Status.LIVE,
        ):
            return Response({'detail': '直播已结束'}, status=400)
        session.status = LiveSession.Status.STOPPED
        session.end_time = timezone.now()
        session.save(update_fields=['status', 'end_time'])
        if session.device_id:
            session.device.status = Device.Status.ONLINE
            session.device.save(update_fields=['status', 'updated_at'])
        return Response({'session_id': session.id, 'status': session.status})


class PersonalLiveDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get('session_id')
        session = LiveSession.objects.filter(pk=session_id).first()
        if not session:
            return Response({'detail': '直播不存在'}, status=404)
        if not _can_manage_live(request.user, session):
            return Response({'detail': '没有权限'}, status=403)
        if session.status in (LiveSession.Status.STARTING, LiveSession.Status.LIVE):
            return Response({'detail': '直播进行中不能删除'}, status=400)
        session.delete()
        return Response({'session_id': session_id}, status=200)
