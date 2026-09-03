# settings_app/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_save


class SettingsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_app'
    verbose_name = 'Currency Settings'

    def ready(self):
        """Initialize app and register signals"""
        from payment.models import Payment
        from email_service import send_payment_notification
        from settings_app.models import EmailNotificationSettings

        def handle_payment_created(sender, instance, created, **kwargs):
            """Send email notification when payment is created"""
            if not created:
                return

            try:
                settings = EmailNotificationSettings.get_settings()
                if settings.notify_on_payment:
                    # Send email synchronously
                    send_payment_notification(instance.id)
            except Exception as e:
                import logging
                logging.exception(f'Error handling payment signal: {e}')

        # Register the signal handler
        post_save.connect(handle_payment_created, sender=Payment, dispatch_uid='payment_email_notification')
