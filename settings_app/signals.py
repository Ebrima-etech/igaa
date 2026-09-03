"""Signal handlers for email notifications"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender='payment.Payment')
def send_email_on_payment_created(sender, instance, created, **kwargs):
    """Send email notification when payment is created"""
    logger.warning(f'🔔 SIGNAL FIRED: payment_id={instance.id}, created={created}, reference={instance.reference_number}')

    if not created:
        logger.warning(f'Payment {instance.id} was updated (not created). Skipping email.')
        return

    try:
        logger.info(f'Payment {instance.id} created. Attempting to send email notification.')

        # Import settings here to avoid circular imports
        from settings_app.models import EmailNotificationSettings
        settings = EmailNotificationSettings.get_settings()

        logger.info(f'Settings loaded: notify_on_payment={settings.notify_on_payment}')

        if not settings.notify_on_payment:
            logger.info('Payment notifications are disabled in settings')
            return

        # Import and call email service
        from email_service import send_payment_notification
        logger.info(f'Calling send_payment_notification for payment {instance.id}')

        result = send_payment_notification(instance.id)
        logger.info(f'✓ Email notification result: {result}')

    except Exception as e:
        logger.exception(f'✗ Error in payment signal handler: {e}')
        import traceback
        logger.error(traceback.format_exc())
