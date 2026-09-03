# igaa/email_service.py
"""Email notification service for payments and receipts"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import logging
from time import sleep

from settings_app.models import EmailNotification, EmailNotificationSettings

logger = logging.getLogger(__name__)


def should_send_notification(notification_type: str) -> bool:
    """Check if notifications should be sent for this type"""
    try:
        settings = EmailNotificationSettings.get_settings()

        if not settings.enable_notifications:
            logger.info(f'Notifications disabled for {notification_type}')
            return False

        if notification_type == 'payment' and not settings.notify_on_payment:
            logger.info('Payment notifications disabled')
            return False

        if notification_type == 'receipt' and not settings.notify_on_receipt:
            logger.info('Receipt notifications disabled')
            return False

        return True
    except Exception as e:
        logger.exception(f'Error checking notification settings: {str(e)}')
        return False


def get_active_recipients() -> list:
    """Get all active email recipients"""
    try:
        emails = list(EmailNotification.objects.filter(
            is_active=True
        ).values_list('email', flat=True))
        logger.info(f'Found {len(emails)} active email recipients')
        return emails
    except Exception as e:
        logger.exception(f'Error getting active recipients: {str(e)}')
        return []


def send_payment_notification(payment_id: int):
    """Send email notification for new payment (synchronous)"""
    if not should_send_notification('payment'):
        logger.info(f'Payment notifications disabled, skipping for payment {payment_id}')
        return False

    try:
        from payment.models import Payment
        from banks.models import BankPaymentSubmission

        payment = Payment.objects.get(id=payment_id)
        settings = EmailNotificationSettings.get_settings()
        recipients = get_active_recipients()

        if not recipients:
            logger.warning(f'No active recipients for payment notification {payment_id}')
            return False

        # Get BankPaymentSubmission ID to build link to payment details
        payment_url = "#"
        try:
            submission = BankPaymentSubmission.objects.get(reference_number=payment.reference_number)
            payment_url = f"https://iga-blush.vercel.app/dashboard/payments/{submission.id}"
        except BankPaymentSubmission.DoesNotExist:
            logger.warning(f'BankPaymentSubmission not found for reference {payment.reference_number}')

        context = {
            'payment': payment,
            'pilgrim_name': getattr(payment.pilgrim, 'full_name', 'Unknown') if hasattr(payment, 'pilgrim') else 'Unknown',
            'amount': payment.amount,
            'reference': payment.reference_number,
            'date': payment.created_at,  # Use created_at (DateTime) instead of payment_date (Date)
            'status': payment.status,
            'payment_url': payment_url,
        }

        html_message = render_to_string('emails/payment_notification.html', context)

        # Use EMAIL_HOST_USER instead of custom email_from to match Gmail authentication
        from django.conf import settings as django_settings
        from_email = django_settings.EMAIL_HOST_USER or settings.email_from

        send_mail(
            subject=f"{settings.email_subject} - Payment Received",
            message=f"Payment received for {context['pilgrim_name']}: {payment.amount}",
            from_email=from_email,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f'✓ Payment notification sent for payment {payment_id} to {len(recipients)} recipients')
        return True

    except Exception as e:
        logger.exception(f'Error sending payment notification for payment {payment_id}: {str(e)}')
        return False


def send_receipt_notification(receipt_id: int):
    """Send email notification for new receipt (synchronous)"""
    if not should_send_notification('receipt'):
        logger.info(f'Receipt notifications disabled, skipping for receipt {receipt_id}')
        return False

    try:
        from igaa_project.models import Receipt
        from django.conf import settings as django_settings

        receipt = Receipt.objects.get(id=receipt_id)
        settings = EmailNotificationSettings.get_settings()
        recipients = get_active_recipients()

        if not recipients:
            logger.warning(f'No active recipients for receipt notification {receipt_id}')
            return False

        context = {
            'receipt': receipt,
            'receipt_number': receipt.receipt_number,
            'payment_reference': receipt.payment_reference,
            'date': receipt.created_at,
        }

        html_message = render_to_string('emails/receipt_notification.html', context)

        # Use EMAIL_HOST_USER instead of custom email_from to match Gmail authentication
        from_email = django_settings.EMAIL_HOST_USER or settings.email_from

        send_mail(
            subject=f"{settings.email_subject} - Receipt Generated",
            message=f"Receipt generated: {receipt.receipt_number}",
            from_email=from_email,
            recipient_list=recipients,
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f'✓ Receipt notification sent for receipt {receipt_id} to {len(recipients)} recipients')
        return True

    except Exception as e:
        logger.exception(f'Error sending receipt notification for receipt {receipt_id}: {str(e)}')
        return False


def send_test_email(recipient_email: str) -> bool:
    """Send a test email to verify configuration"""
    try:
        from django.conf import settings as django_settings

        settings = EmailNotificationSettings.get_settings()

        # Use EMAIL_HOST_USER instead of custom email_from to match Gmail authentication
        from_email = django_settings.EMAIL_HOST_USER or settings.email_from

        send_mail(
            subject=f"Test Email - {settings.email_subject}",
            message="This is a test email to verify the Gmail configuration is working correctly.",
            from_email=from_email,
            recipient_list=[recipient_email],
            html_message="""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Test Email</h2>
                    <p>This is a test email to verify the Gmail configuration is working correctly.</p>
                    <p><strong>Status:</strong> If you received this email, your email configuration is working! ✓</p>
                </body>
            </html>
            """,
            fail_silently=False,
        )

        logger.info(f'✓ Test email sent to {recipient_email}')
        return True

    except Exception as e:
        logger.exception(f'Error sending test email to {recipient_email}: {str(e)}')
        return False
