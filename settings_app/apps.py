# settings_app/apps.py
from django.apps import AppConfig


class SettingsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_app'
    verbose_name = 'Currency Settings'

    def ready(self):
        """Initialize app and register signals"""
        try:
            import igaa.signals  # Import signals for email notifications
        except ImportError:
            pass
