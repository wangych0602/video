from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from rest_framework.test import APITestCase

from schools.models import School
from users.models import TeacherProfile
from videos.models import Video

from .models import Device, LiveSession

User = get_user_model()


class DeviceWorkflowTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(name='测试学校')
        self.admin = User.objects.create_superuser(username='admin1', password='pass12345', email='admin1@example.com')
        self.admin.role = User.Role.ADMIN
        self.admin.save(update_fields=['role'])

    def _register(self, sn='SN-001', name='录播主机1'):
        return self.client.post(
            '/api/devices/register/',
            {
                'device_sn': sn,
                'device_name': name,
                'device_type': Device.DeviceType.RECORDING_HOST,
                'manufacturer': '测试厂商',
                'school': self.school.id,
            },
            format='json',
        )

    def _heartbeat(self, sn, token):
        return self.client.post(
            '/api/devices/heartbeat/',
            {'device_sn': sn, 'ip_address': '192.168.1.10'},
            HTTP_X_DEVICE_TOKEN=token,
            format='json',
        )

    def test_device_register_returns_token(self):
        resp = self._register()
        self.assertEqual(resp.status_code, 201)
        data = resp.data
        self.assertIn('device_id', data)
        self.assertTrue(data['device_token'])
        device = Device.objects.get(device_sn='SN-001')
        self.assertEqual(device.device_token, data['device_token'])
        self.assertEqual(device.status, Device.Status.OFFLINE)

    def test_register_same_sn_returns_same_token(self):
        first = self._register()
        second = self._register()
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data['device_id'], second.data['device_id'])
        self.assertEqual(first.data['device_token'], second.data['device_token'])

    def test_heartbeat_updates_online(self):
        register = self._register()
        resp = self._heartbeat('SN-001', register.data['device_token'])
        self.assertEqual(resp.status_code, 200)
        device = Device.objects.get(device_sn='SN-001')
        self.assertEqual(device.status, Device.Status.ONLINE)
        self.assertIsNotNone(device.last_online_time)
        self.assertEqual(str(device.ip_address), '192.168.1.10')

    def test_heartbeat_rejects_wrong_token(self):
        self._register()
        resp = self._heartbeat('SN-001', 'wrong-token')
        self.assertEqual(resp.status_code, 401)

    def test_start_live_requires_online_device(self):
        self._register()
        self.client.force_authenticate(self.admin)
        device = Device.objects.get(device_sn='SN-001')
        resp = self.client.post(f'/api/devices/{device.id}/start-live/')
        self.assertEqual(resp.status_code, 400)

    def test_full_live_flow(self):
        register = self._register()
        self._heartbeat('SN-001', register.data['device_token'])
        device = Device.objects.get(device_sn='SN-001')
        self.client.force_authenticate(self.admin)

        resp = self.client.post(f'/api/devices/{device.id}/start-live/', {'title': '数学课直播'})
        self.assertEqual(resp.status_code, 200)
        data = resp.data
        self.assertIn('stream_key', data)
        self.assertIn(data['stream_key'], data['stream_url'])
        self.assertTrue(data['hls_url'].endswith(f'{data["stream_key"]}.m3u8'))
        session = LiveSession.objects.get(id=data['session_id'])
        self.assertEqual(session.status, LiveSession.Status.STARTING)
        device.refresh_from_db()
        self.assertEqual(device.status, Device.Status.STREAMING)

        callback = self.client.post(
            '/api/live/callback/',
            {'stream_key': data['stream_key'], 'event': 'stream_started'},
            format='json',
        )
        self.assertEqual(callback.status_code, 200)
        session.refresh_from_db()
        self.assertEqual(session.status, LiveSession.Status.LIVE)
        self.assertIsNotNone(session.start_time)

        stop = self.client.post(f'/api/devices/{device.id}/stop-live/')
        self.assertEqual(stop.status_code, 200)
        session.refresh_from_db()
        self.assertEqual(session.status, LiveSession.Status.STOPPED)
        self.assertIsNotNone(session.end_time)
        device.refresh_from_db()
        self.assertEqual(device.status, Device.Status.ONLINE)

    def test_upload_video_creates_video_record(self):
        register = self._register()
        self._heartbeat('SN-001', register.data['device_token'])
        payload = SimpleUploadedFile('recording.mp4', b'fake-mp4-content', content_type='video/mp4')
        resp = self.client.post(
            '/api/devices/upload-video/',
            {
                'device_sn': 'SN-001',
                'record_time': '2026-08-01 09:00:00',
                'video_file': payload,
            },
            HTTP_X_DEVICE_TOKEN=register.data['device_token'],
            format='multipart',
        )
        self.assertEqual(resp.status_code, 201)
        video = Video.objects.get(id=resp.data['id'])
        self.assertEqual(video.school, self.school)
        self.assertEqual(video.status, Video.Status.PENDING)
        self.assertGreater(video.file_size, 0)

    def test_callback_stream_error_sets_device_error(self):
        register = self._register()
        self._heartbeat('SN-001', register.data['device_token'])
        device = Device.objects.get(device_sn='SN-001')
        self.client.force_authenticate(self.admin)
        resp = self.client.post(f'/api/devices/{device.id}/start-live/')
        stream_key = resp.data['stream_key']
        callback = self.client.post(
            '/api/live/callback/',
            {'stream_key': stream_key, 'event': 'stream_error'},
            format='json',
        )
        self.assertEqual(callback.status_code, 200)
        session = LiveSession.objects.get(id=resp.data['session_id'])
        self.assertEqual(session.status, LiveSession.Status.ERROR)
        device.refresh_from_db()
        self.assertEqual(device.status, Device.Status.ERROR)


class TeacherDeviceAccessTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(name='A校')
        self.other_school = School.objects.create(name='B校')
        self.teacher = User.objects.create_user(
            username='teacher3',
            password='pass12345',
            role=User.Role.TEACHER,
            school=self.school,
        )
        TeacherProfile.objects.create(user=self.teacher, school=self.school)
        self.device = Device.objects.create(
            device_sn='SN-T1',
            device_name='教室设备',
            device_type=Device.DeviceType.RECORDING_HOST,
            school=self.school,
        )
        self.other_device = Device.objects.create(
            device_sn='SN-T2',
            device_name='他校设备',
            device_type=Device.DeviceType.RECORDING_HOST,
            school=self.other_school,
        )

    def test_teacher_lists_school_devices(self):
        self.client.force_authenticate(self.teacher)
        resp = self.client.get('/api/devices/my-school/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['device_sn'], 'SN-T1')

    def test_teacher_start_live_on_school_device(self):
        self.device.status = Device.Status.ONLINE
        self.device.save(update_fields=['status'])
        self.client.force_authenticate(self.teacher)
        resp = self.client.post(f'/api/devices/{self.device.id}/start-live/', {'title': '我的课堂'}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('stream_key', resp.data)

    def test_teacher_cannot_start_live_on_other_school_device(self):
        self.other_device.status = Device.Status.ONLINE
        self.other_device.save(update_fields=['status'])
        self.client.force_authenticate(self.teacher)
        resp = self.client.post(f'/api/devices/{self.other_device.id}/start-live/', format='json')
        self.assertEqual(resp.status_code, 401)

    def test_teacher_personal_live_flow(self):
        self.client.force_authenticate(self.teacher)
        resp = self.client.post('/api/live/personal-start/', {'title': '我的个人直播'}, format='json')
        self.assertEqual(resp.status_code, 201)
        data = resp.data
        self.assertIn('push_token', data)
        self.assertTrue(data['stream_url'].endswith(data['stream_key']))
        self.assertEqual(data['stream_key'].rsplit('_', 1)[-1], data['push_token'])
        session = LiveSession.objects.get(id=data['session_id'])
        self.assertIsNone(session.device)
        self.assertEqual(session.school_id, self.school.id)
        self.assertEqual(session.stream_token, data['push_token'])
        self.assertEqual(session.status, LiveSession.Status.CREATED)

        bad = self.client.post(
            '/api/live/callback/',
            {'stream_key': data['stream_key'], 'event': 'publish_started', 'token': 'wrong-token'},
            format='json',
        )
        self.assertEqual(bad.status_code, 403)

        ok = self.client.post(
            '/api/live/callback/',
            {'stream_key': data['stream_key'], 'event': 'publish_started'},
            format='json',
        )
        self.assertEqual(ok.status_code, 200)
        session.refresh_from_db()
        self.assertEqual(session.status, LiveSession.Status.LIVE)
        self.assertEqual(session.stream_token, '')
        self.assertTrue(session.token_used)

        again = self.client.post(
            '/api/live/callback/',
            {'stream_key': data['stream_key'], 'event': 'publish_started'},
            format='json',
        )
        self.assertEqual(again.status_code, 403)

        stop = self.client.post(
            '/api/live/callback/',
            {'stream_key': data['stream_key'], 'event': 'publish_stopped'},
            format='json',
        )
        self.assertEqual(stop.status_code, 200)
        session.refresh_from_db()
        self.assertEqual(session.status, LiveSession.Status.STOPPED)
        self.assertIsNotNone(session.end_time)

    def _start_personal(self):
        resp = self.client.post('/api/live/personal-start/', {'title': '我的个人直播'}, format='json')
        self.assertEqual(resp.status_code, 201)
        return resp.data['session_id']

    def test_teacher_stops_own_personal_live(self):
        self.client.force_authenticate(self.teacher)
        session_id = self._start_personal()
        resp = self.client.post('/api/live/personal-stop/', {'session_id': session_id}, format='json')
        self.assertEqual(resp.status_code, 200)
        session = LiveSession.objects.get(id=session_id)
        self.assertEqual(session.status, LiveSession.Status.STOPPED)
        self.assertIsNotNone(session.end_time)

    def test_teacher_deletes_own_stopped_live(self):
        self.client.force_authenticate(self.teacher)
        session_id = self._start_personal()
        self.client.post('/api/live/personal-stop/', {'session_id': session_id}, format='json')
        resp = self.client.post('/api/live/personal-delete/', {'session_id': session_id}, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(LiveSession.objects.filter(id=session_id).exists())

    def test_teacher_cannot_manage_other_teacher_live(self):
        other = User.objects.create_user(username='teacher4', password='pass12345', role=User.Role.TEACHER, school=self.other_school)
        TeacherProfile.objects.create(user=other, school=self.other_school)
        self.client.force_authenticate(other)
        session_id = self._start_personal()
        self.client.force_authenticate(self.teacher)
        stop = self.client.post('/api/live/personal-stop/', {'session_id': session_id}, format='json')
        self.assertEqual(stop.status_code, 403)
        delete = self.client.post('/api/live/personal-delete/', {'session_id': session_id}, format='json')
        self.assertEqual(delete.status_code, 403)

    def test_mine_live_sessions_only_own(self):
        self.client.force_authenticate(self.teacher)
        own_id = self._start_personal()
        other = User.objects.create_user(username='teacher5', password='pass12345', role=User.Role.TEACHER, school=self.other_school)
        TeacherProfile.objects.create(user=other, school=self.other_school)
        self.client.force_authenticate(other)
        self._start_personal()
        self.client.force_authenticate(self.teacher)
        resp = self.client.get('/api/live-sessions/?mine=1')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['id'], own_id)

    def test_student_cannot_start_personal_live(self):
        student = User.objects.create_user(
            username='student1',
            password='pass12345',
            role=User.Role.STUDENT,
            school=self.school,
        )
        self.client.force_authenticate(student)
        resp = self.client.post('/api/live/personal-start/', {}, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_anonymous_cannot_list_school_devices(self):
        resp = self.client.get('/api/devices/my-school/')
        self.assertEqual(resp.status_code, 401)


class StreamingInfrastructureTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(name='流媒体学校')
        self.admin = User.objects.create_superuser(username='admin2', password='pass12345', email='admin2@example.com')
        self.admin.role = User.Role.ADMIN
        self.admin.save(update_fields=['role'])
        register = self.client.post(
            '/api/devices/register/',
            {
                'device_sn': 'STREAM-001',
                'device_name': '直播录播机',
                'device_type': Device.DeviceType.RECORDING_HOST,
                'school': self.school.id,
            },
            format='json',
        )
        self.token = register.data['device_token']
        self.client.post(
            '/api/devices/heartbeat/',
            {'device_sn': 'STREAM-001'},
            HTTP_X_DEVICE_TOKEN=self.token,
            format='json',
        )
        self.device = Device.objects.get(device_sn='STREAM-001')
        self.client.force_authenticate(self.admin)
        resp = self.client.post(f'/api/devices/{self.device.id}/start-live/', {'title': '智慧课堂直播'})
        self.session = LiveSession.objects.get(id=resp.data['session_id'])
        self.stream_key = resp.data['stream_key']

    def test_live_urls_format(self):
        self.assertIn('/live/', self.session.rtmp_push_url)
        self.assertTrue(self.session.rtmp_push_url.startswith('rtmp://'))
        self.assertTrue(self.session.hls_url.startswith('http://'))
        self.assertTrue(self.session.hls_url.endswith(f'{self.stream_key}.m3u8'))

    def test_callback_publish_events(self):
        resp = self.client.post(
            '/api/live/callback/',
            {'stream_key': self.stream_key, 'event': 'publish_started'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, LiveSession.Status.LIVE)
        resp = self.client.post(
            '/api/live/callback/',
            {'stream_key': self.stream_key, 'event': 'publish_stopped'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, LiveSession.Status.STOPPED)
        self.device.refresh_from_db()
        self.assertEqual(self.device.status, Device.Status.ONLINE)

    def test_callback_accepts_nginx_form(self):
        resp = self.client.post(
            '/api/live/callback/',
            {'name': self.stream_key, 'call': 'publish'},
        )
        self.assertEqual(resp.status_code, 200)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, LiveSession.Status.LIVE)

    def test_stream_detection_marks_error_when_stream_down(self):
        self.client.post(
            '/api/live/callback/',
            {'stream_key': self.stream_key, 'event': 'publish_started'},
            format='json',
        )
        with patch('devices.management.commands.check_live_streams.check_hls_url', return_value=False):
            call_command('check_live_streams')
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, LiveSession.Status.ERROR)
        self.device.refresh_from_db()
        self.assertEqual(self.device.status, Device.Status.ERROR)

    def test_stream_detection_keeps_live_when_stream_up(self):
        self.client.post(
            '/api/live/callback/',
            {'stream_key': self.stream_key, 'event': 'publish_started'},
            format='json',
        )
        with patch('devices.management.commands.check_live_streams.check_hls_url', return_value=True):
            call_command('check_live_streams')
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, LiveSession.Status.LIVE)

    def test_m3u8_access_simulation(self):
        from devices.management.commands.check_live_streams import check_hls_url

        with patch('urllib.request.urlopen') as mock_open:
            mock_open.return_value.__enter__.return_value.status = 200
            self.assertTrue(check_hls_url('http://127.0.0.1:8080/hls/demo.m3u8'))
