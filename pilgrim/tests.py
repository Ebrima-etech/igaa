from django.test import TestCase
from .models import Pilgrim


class PilgrimTestCase(TestCase):
    def setUp(self):
        self.pilgrim = Pilgrim.objects.create(
            registration_id='P001',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+22090000000',
            date_of_birth='1990-01-01',
            gender='M',
            nationality='Gambian',
            passport_number='A12345678',
            address='123 Main St',
            city='Banjul',
            state='Banjul',
            postal_code='10001',
            country='Gambia',
        )

    def test_pilgrim_creation(self):
        self.assertEqual(self.pilgrim.full_name, 'John Doe')
        self.assertEqual(self.pilgrim.status, 'registered')
