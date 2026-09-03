# igaa/signals.py
"""Signal handlers for automated email notifications"""

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from payment.models import Payment
from settings_app.models import EmailNotificationSettings

try:
    from igaa.email_service import send_payment_notification, send_receipt_notification
except ImportError:
    # Fallback if module path is different
    try:
        from email_service import send_payment_notification, send_receipt_notification
    except ImportError:
        send_payment_notification = None
        send_receipt_notification = None

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Payment)
def handle_payment_created(sender, instance, created, **kwargs):
    """Trigger email notification when payment is created (synchronous)"""
    if created:
        try:
            if not send_payment_notification:
                logger.warning('Email service not available, skipping notification')
                return

            settings = EmailNotificationSettings.get_settings()
            if settings.notify_on_payment:
                logger.info(f'Payment created: {instance.id}. Sending notification.')

                # Apply delay if configured
                if settings.notification_delay > 0:
                    from time import sleep
                    delay_seconds = settings.notification_delay * 60
                    logger.info(f'Delaying notification by {settings.notification_delay} minutes')
                    sleep(delay_seconds)

                # Send email synchronously
                result = send_payment_notification(instance.id)
                if result:
                    logger.info(f'✓ Payment notification sent successfully for payment {instance.id}')
                else:
                    logger.warning(f'Payment notification failed for payment {instance.id}')
            else:
                logger.info('Payment notifications disabled, skipping notification')

        except Exception as e:
            logger.exception(f'Error handling payment creation signal for payment {instance.id}: {str(e)}')


# Uncomment this when Receipt model is available in a separate app
# from igaa_project.models import Receipt
#
# @receiver(post_save, sender=Receipt)
# def handle_receipt_created(sender, instance, created, **kwargs):
#     """Trigger email notification when receipt is created"""
#     if created:
#         try:
#             settings = EmailNotificationSettings.get_settings()
#             if settings.notify_on_receipt:
#                 logger.info(f'Receipt created: {instance.id}. Queuing notification.')
#
#                 # Apply delay if configured
#                 if settings.notification_delay > 0:
#                     send_receipt_notification.apply_async(
#                         args=[instance.id],
#                         countdown=settings.notification_delay * 60
#                     )
#                     logger.info(f'Receipt notification scheduled with {settings.notification_delay} minute delay')
#                 else:
#                     send_receipt_notification.delay(instance.id)
#                     logger.info('Receipt notification queued for immediate sending')
#             else:
#                 logger.info('Receipt notifications disabled, skipping notification')
#
#         except Exception as e:
#             logger.exception(f'Error handling receipt creation signal for receipt {instance.id}: {str(e)}')
