#!/usr/bin/env python
"""Simple email test without database dependency"""

import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'igaa_project.settings')

import django
django.setup()

from django.core.mail import send_mail

print("\n" + "="*70)
print("SIMPLE EMAIL TEST (No Database Required)")
print("="*70)

print("\n[Configuration Check]")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

if not settings.EMAIL_HOST_USER:
    print("\n[ERROR] EMAIL_HOST_USER is not set!")
    exit(1)

if not settings.EMAIL_HOST_PASSWORD:
    print("\n[ERROR] EMAIL_HOST_PASSWORD is not set!")
    exit(1)

print("\n[Attempting Email Test]")
print("Sending test email to test@example.com...")

try:
    result = send_mail(
        subject="Django SMTP Test",
        message="If you received this, Gmail SMTP is working!",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['test@example.com'],
        fail_silently=False,
    )
    print("[SUCCESS] Email sent!")
    print("\nNote: This test sent to test@example.com (fake address)")
    print("But if there were no errors, it means Gmail SMTP is working!\n")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}\n")
    print("Common solutions:")
    print("1. Check if Gmail credentials are correct")
    print("2. Enable 2FA on Gmail account")
    print("3. Generate App Password: https://myaccount.google.com/apppasswords")
    print("4. Check firewall isn't blocking SMTP port 587")
    print("5. Verify .env file has correct EMAIL_HOST_PASSWORD\n")

print("="*70 + "\n")
