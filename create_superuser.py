import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'igaa_project.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✓ Superuser 'admin' created successfully")
    print("✓ Username: admin")
    print("✓ Password: admin123")
else:
    print("✓ Superuser 'admin' already exists")
    print("✓ Username: admin")
    print("✓ Password: admin123")
