# igaa/signals.py
"""Signal handlers for automated email notifications"""

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

from payment.models import Payment
from settings_app.models import EmailNotificationSettings
from email_service import send_payment_notification, send_receipt_notification

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Payment)
def handle_payment_created(sender, instance, created, **kwargs):
    """Trigger email notification when payment is created"""
    if created:
        try:
            settings = EmailNotificationSettings.get_settings()
            if settings.notify_on_payment:
                logger.info(f'Payment created: {instance.id}. Queuing notification.')

                # Apply delay if configured
                if settings.notification_delay > 0:
                    send_payment_notification.apply_async(
                        args=[instance.id],
                        countdown=settings.notification_delay * 60  # Convert minutes to seconds
                    )
                    logger.info(f'Payment notification scheduled with {settings.notification_delay} minute delay')
                else:
                    send_payment_notification.delay(instance.id)
                    logger.info('Payment notification queued for immediate sending')
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
