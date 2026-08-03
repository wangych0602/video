from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from schools.models import School

User = get_user_model()


class UserApiTests(APITestCase):
    def setUp(self):
        self.school = School.objects.create(name='测试学校')
        self.admin = User.objects.create_superuser(username='admin1', password='pass12345', email='admin1@example.com')
        self.admin.role = User.Role.ADMIN
        self.admin.save(update_fields=['role'])

    def test_login_returns_token(self):
        resp = self.client.post(
            '/api/auth/login/',
            {'username': 'admin1', 'password': 'pass12345'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['username'], 'admin1')

    def test_anonymous_cannot_list_users(self):
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, 401)

    def test_admin_creates_user_with_hashed_password(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post(
            '/api/users/',
            {
                'username': 'teacher5',
                'email': 'teacher5@example.com',
                'password': 'secret123',
                'role': User.Role.TEACHER,
                'school': self.school.id,
            },
            format='json',
        )
        self.assertEqual(resp.status_code, 201)
        user = User.objects.get(username='teacher5')
        self.assertTrue(user.check_password('secret123'))
        self.assertNotEqual(user.password, 'secret123')
        self.assertEqual(user.school_id, self.school.id)

    def test_non_admin_cannot_create_user(self):
        teacher = User.objects.create_user(username='t6', password='pass12345', role=User.Role.TEACHER)
        self.client.force_authenticate(teacher)
        resp = self.client.post('/api/users/', {'username': 'x', 'password': 'y'}, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_anonymous_can_list_schools_but_not_create(self):
        resp = self.client.get('/api/schools/')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post('/api/schools/', {'name': '新学校'}, format='json')
        self.assertEqual(resp.status_code, 401)

    def test_teacher_cannot_create_school(self):
        teacher = User.objects.create_user(username='t7', password='pass12345', role=User.Role.TEACHER)
        self.client.force_authenticate(teacher)
        resp = self.client.post('/api/schools/', {'name': '新学校', 'country': 'CN'}, format='json')
        self.assertEqual(resp.status_code, 403)
