from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserRole


class UserRoleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.role = UserRole.objects.create(user=self.user, role='hajj_admin')

    def test_user_role_creation(self):
        self.assertEqual(self.role.role, 'hajj_admin')
        self.assertEqual(self.role.user.username, 'testuser')
