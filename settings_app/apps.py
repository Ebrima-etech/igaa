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
        logger.info('settings_app.ready() called - registering payment signal')

        try:
            from django.apps import apps

            # Use apps.get_model to avoid import timing issues
            Payment = apps.get_model('payment', 'Payment')
            EmailNotificationSettings = apps.get_model('settings_app', 'EmailNotificationSettings')

            def handle_payment_created(sender, instance, created, **kwargs):
                """Send email notification when payment is created"""
                logger.info(f'Signal fired: payment {instance.id}, created={created}')

                if not created:
                    logger.info(f'Payment {instance.id} was updated, not created. Skipping.')
                    return

                try:
                    # Import here to avoid circular imports
                    import sys
                    import os
                    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

                    from email_service import send_payment_notification

                    settings = EmailNotificationSettings.get_settings()
                    logger.info(f'Notification settings: notify_on_payment={settings.notify_on_payment}')

                    if settings.notify_on_payment:
                        logger.info(f'Sending payment notification for payment {instance.id}')
                        result = send_payment_notification(instance.id)
                        logger.info(f'Payment notification result: {result}')
                    else:
                        logger.info('Payment notifications are disabled')
                except Exception as e:
                    logger.exception(f'Error handling payment signal: {e}')

            # Register the signal handler
            logger.info('Attempting to register post_save signal for Payment model')
            post_save.connect(
                handle_payment_created,
                sender=Payment,
                dispatch_uid='payment_email_notification'
            )
            logger.info('✓ Payment email notification signal registered successfully')

        except Exception as e:
            logger.exception(f'✗ Failed to register payment signal: {e}')
