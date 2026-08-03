from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from schools.models import School
from users.models import TeacherProfile

from .models import ReviewLog, Video, VideoCategory, VideoSetting

User = get_user_model()


class VideoWorkflowTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(name='测试学校')
        self.category = VideoCategory.objects.create(name='课堂实录', description='课堂录像')
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='pass12345',
            role=User.Role.TEACHER,
        )
        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher,
            school=self.school,
            subject='数学',
        )
        self.other_teacher = User.objects.create_user(
            username='teacher2',
            password='pass12345',
            role=User.Role.TEACHER,
        )
        TeacherProfile.objects.create(user=self.other_teacher, school=self.school, subject='语文')
        self.admin = User.objects.create_superuser(
            username='admin1',
            password='pass12345',
            email='admin1@example.com',
        )
        self.admin.role = User.Role.ADMIN
        self.admin.save(update_fields=['role'])

    def _upload(self, client, filename='lesson.mp4'):
        payload = SimpleUploadedFile(filename, b'fake-mp4-content', content_type='video/mp4')
        return client.post(
            '/api/videos/upload/',
            {
                'title': '数学课实录',
                'description': '第一章',
                'category': self.category.id,
                'file': payload,
            },
            format='multipart',
        )

    def test_teacher_upload_creates_pending_video(self):
        self.client.force_authenticate(self.teacher)
        resp = self._upload(self.client)
        self.assertEqual(resp.status_code, 201)
        video = Video.objects.get()
        self.assertEqual(video.status, Video.Status.PENDING)
        self.assertEqual(video.teacher, self.teacher_profile)
        self.assertEqual(video.school, self.school)
        self.assertGreater(video.file_size, 0)

    def test_upload_without_cover_uses_default_cover(self):
        default_cover = SimpleUploadedFile('default.jpg', b'fake-jpg-content', content_type='image/jpeg')
        VideoSetting.objects.update_or_create(pk=1, defaults={'default_cover': default_cover})
        self.client.force_authenticate(self.teacher)
        payload = SimpleUploadedFile('lesson.mp4', b'fake-mp4-content', content_type='video/mp4')
        resp = self.client.post(
            '/api/videos/upload/',
            {'title': 'cover test', 'file': payload},
            format='multipart',
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data['cover_image'])

    def test_teacher_only_sees_own_videos(self):
        self.client.force_authenticate(self.teacher)
        self._upload(self.client)
        self.client.force_authenticate(self.other_teacher)
        resp = self.client.get('/api/videos/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 0)
        self.client.force_authenticate(self.teacher)
        resp = self.client.get('/api/videos/my/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)

    def test_teacher_cannot_approve_video(self):
        self.client.force_authenticate(self.teacher)
        self._upload(self.client)
        video = Video.objects.get()
        resp = self.client.post(f'/api/videos/{video.id}/approve/')
        self.assertEqual(resp.status_code, 403)

    def test_anonymous_can_list_published_videos_only(self):
        self.client.force_authenticate(self.teacher)
        self._upload(self.client)
        video = Video.objects.get()
        video.status = Video.Status.PUBLISHED
        video.save(update_fields=['status'])
        self.client.force_authenticate(user=None)
        resp = self.client.get('/api/videos/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['status'], Video.Status.PUBLISHED)

    def test_anonymous_cannot_upload_video(self):
        payload = SimpleUploadedFile('lesson.mp4', b'fake-mp4-content', content_type='video/mp4')
        resp = self.client.post(
            '/api/videos/upload/',
            {'title': '匿名上传', 'file': payload},
            format='multipart',
        )
        self.assertEqual(resp.status_code, 401)

    def test_admin_approve_auto_publishes(self):
        self.client.force_authenticate(self.teacher)
        self._upload(self.client)
        video = Video.objects.get()
        self.client.force_authenticate(self.admin)
        resp = self.client.post(f'/api/videos/{video.id}/approve/', {'comment': '内容无误'})
        self.assertEqual(resp.status_code, 200)
        video.refresh_from_db()
        self.assertEqual(video.status, Video.Status.PUBLISHED)
        self.assertEqual(ReviewLog.objects.filter(action=ReviewLog.Action.PUBLISHED).count(), 1)

    def test_admin_reject_requires_comment(self):
        self.client.force_authenticate(self.teacher)
        upload_resp = self._upload(self.client)
        self.assertEqual(upload_resp.status_code, 201)
        video = Video.objects.get(id=upload_resp.data['id'])
        self.client.force_authenticate(self.admin)
        resp = self.client.post(f'/api/videos/{video.id}/reject/')
        self.assertEqual(resp.status_code, 400)
        resp = self.client.post(f'/api/videos/{video.id}/reject/', {'comment': '画面不清晰'})
        self.assertEqual(resp.status_code, 200)
        video.refresh_from_db()
        self.assertEqual(video.status, Video.Status.REJECTED)
        self.assertEqual(ReviewLog.objects.filter(action=ReviewLog.Action.REJECTED).count(), 1)

    def test_upload_rejects_unsupported_extension(self):
        self.client.force_authenticate(self.teacher)
        payload = SimpleUploadedFile('notes.txt', b'not a video', content_type='text/plain')
        resp = self.client.post(
            '/api/videos/upload/',
            {'title': '非法文件', 'file': payload},
            format='multipart',
        )
        self.assertEqual(resp.status_code, 400)

    def test_public_site_settings(self):
        resp = self.client.get('/api/site-settings/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('site_name', resp.data)
