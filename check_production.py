#!/usr/bin/env python
"""
Production readiness checker for Render deployment.
Run: python check_production.py
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check that all required packages are in requirements.txt"""
    required = [
        'Django==4.2',
        'djangorestframework==3.14',
        'gunicorn==21.2',
        'psycopg2-binary',
        'whitenoise',
        'dj-database-url',
    ]

    req_file = Path('requirements.txt')
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False

    content = req_file.read_text()
    all_found = True
    for pkg in required:
        if pkg.split('==')[0] not in content:
            print(f"❌ Missing: {pkg}")
            all_found = False

    if all_found:
        print("✅ All required packages in requirements.txt")
    return all_found

def check_settings():
    """Check that settings.py has production configurations"""
    from igaa_project import settings

    checks = [
        ('DEBUG', lambda: not settings.DEBUG, "DEBUG should be False"),
        ('SECRET_KEY', lambda: settings.SECRET_KEY != 'django-insecure-change-me-in-production', "SECRET_KEY is default"),
        ('ALLOWED_HOSTS', lambda: '*.onrender.com' in settings.ALLOWED_HOSTS or len(settings.ALLOWED_HOSTS) > 2, "ALLOWED_HOSTS should include render domain"),
        ('WhiteNoise', lambda: 'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE, "WhiteNoise not in MIDDLEWARE"),
        ('Database Config', lambda: hasattr(settings, 'DATABASES') and settings.DATABASES, "Database not configured"),
    ]

    all_passed = True
    for name, check_fn, error_msg in checks:
        try:
            if check_fn():
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: {error_msg}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_passed = False

    return all_passed

def check_files():
    """Check that deployment files exist"""
    files = [
        'Procfile',
        'build.sh',
        'render.yaml',
    ]

    all_found = True
    for f in files:
        if Path(f).exists():
            print(f"✅ {f}: exists")
        else:
            print(f"❌ {f}: missing")
            all_found = False

    return all_found

def main():
    print("🔍 Production Readiness Check for Render Deployment\n")

    results = {
        'Requirements': check_requirements(),
        'Settings': check_settings(),
        'Files': check_files(),
    }

    print("\n" + "="*50)
    print("Summary:")
    print("="*50)
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")

    all_passed = all(results.values())
    print("="*50)

    if all_passed:
        print("\n✅ Ready for Render deployment!")
        return 0
    else:
        print("\n❌ Fix issues above before deploying")
        return 1

if __name__ == '__main__':
    sys.exit(main())
