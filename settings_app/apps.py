# settings_app/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_save
import logging

logger = logging.getLogger(__name__)


class SettingsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_app'
    verbose_name = 'Currency Settings'

    def ready(self):
        """Initialize app and register signals"""
        try:
            from payment.models import Payment
            from settings_app.models import EmailNotificationSettings

            def handle_payment_created(sender, instance, created, **kwargs):
                """Send email notification when payment is created"""
                if not created:
                    return

                try:
                    # Import here to avoid circular imports
                    from email_service import send_payment_notification

                    settings = EmailNotificationSettings.get_settings()
                    if settings.notify_on_payment:
                        logger.info(f'Payment {instance.id} created. Sending email notification.')
                        result = send_payment_notification(instance.id)
                        logger.info(f'Email sent: {result}')
                except Exception as e:
                    logger.exception(f'Error handling payment signal: {e}')

            # Register the signal handler
            post_save.connect(
                handle_payment_created,
                sender=Payment,
                dispatch_uid='payment_email_notification'
            )
            logger.info('Payment email notification signal registered successfully')

        except Exception as e:
            logger.exception(f'Failed to register payment signal: {e}')
