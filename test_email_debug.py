#!/usr/bin/env python
"""Email notification debugging script"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'igaa_project.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from settings_app.models import EmailNotification, EmailNotificationSettings
from email_service import send_test_email, send_payment_notification
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("EMAIL NOTIFICATION SYSTEM - DIAGNOSTIC REPORT")
print("="*70)

# 1. Check Django Email Configuration
print("\n[1] DJANGO EMAIL CONFIGURATION")
print("-" * 70)
print(f"[OK] EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"[OK] EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"[OK] EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"[OK] EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"[OK] EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"[OK] DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
if settings.EMAIL_HOST_PASSWORD:
    print(f"[OK] EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD)}")
else:
    print(f"[ERROR] EMAIL_HOST_PASSWORD: NOT SET!")

# 2. Check Database Tables
print("\n[2] DATABASE TABLES")
print("-" * 70)
try:
    settings_count = EmailNotificationSettings.objects.count()
    recipients_count = EmailNotification.objects.count()
    print(f"[OK] EmailNotificationSettings table: {settings_count} record(s)")
    print(f"[OK] EmailNotification table: {recipients_count} record(s)")
except Exception as e:
    print(f"[ERROR] Database error: {e}")
    print("  Run: python manage.py migrate")
    sys.exit(1)

# 3. Check Notification Settings
print("\n[3] NOTIFICATION SETTINGS")
print("-" * 70)
try:
    settings_obj = EmailNotificationSettings.get_settings()
    print(f"[OK] enable_notifications: {settings_obj.enable_notifications}")
    print(f"[OK] notify_on_payment: {settings_obj.notify_on_payment}")
    print(f"[OK] notify_on_receipt: {settings_obj.notify_on_receipt}")
    print(f"[OK] notification_delay: {settings_obj.notification_delay} minutes")
    print(f"[OK] email_from: {settings_obj.email_from}")
    print(f"[OK] email_subject: {settings_obj.email_subject}")
except Exception as e:
    print(f"[ERROR] Error: {e}")

# 4. Check Email Recipients
print("\n[4] EMAIL RECIPIENTS")
print("-" * 70)
try:
    recipients = EmailNotification.objects.all()
    active_recipients = EmailNotification.objects.filter(is_active=True)

    print(f"[OK] Total recipients: {recipients.count()}")
    print(f"[OK] Active recipients: {active_recipients.count()}")

    if recipients.count() == 0:
        print("\n[WARNING]  WARNING: No email recipients configured!")
        print("   Go to: Dashboard → Settings → Email Notifications")
        print("   Add at least one email address")
    else:
        for email in recipients:
            status = "[OK] ACTIVE" if email.is_active else "[ERROR] INACTIVE"
            print(f"   [{status}] {email.email} - {email.description or 'No description'}")
except Exception as e:
    print(f"[ERROR] Error: {e}")

# 5. Test Basic Email Sending
print("\n[5] BASIC EMAIL TEST")
print("-" * 70)
try:
    print("Attempting to send test email...")
    send_mail(
        subject="Django Email Test",
        message="This is a test email from Django.",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['test@example.com'],
        fail_silently=False,
    )
    print("[OK] Basic email send attempted (check logs)")
except Exception as e:
    print(f"[ERROR] Email send failed: {e}")
    print("\nPossible causes:")
    print("  1. Gmail credentials wrong")
    print("  2. Gmail 2FA not enabled")
    print("  3. App Password not created")
    print("  4. Network/firewall blocking SMTP")

# 6. Test Email Service Function
print("\n[6] EMAIL SERVICE FUNCTION TEST")
print("-" * 70)
if active_recipients.count() == 0:
    print("[WARNING]  Skipped: No active recipients configured")
else:
    try:
        result = send_test_email('etechlearning1@gmail.com')
        if result:
            print("[OK] Test email sent successfully!")
        else:
            print("[ERROR] Test email failed (check logs)")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

print("\n" + "="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70 + "\n")

print("NEXT STEPS:")
print("1. Make sure you added email recipients in the dashboard")
print("2. Check your email inbox (and spam folder)")
print("3. Verify Gmail credentials: python manage.py shell")
print("4. Check Django logs for errors: tail -f logs/django.log")
print()
