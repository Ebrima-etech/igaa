# settings_app/apps.py
from django.apps import AppConfig


class SettingsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_app'
    verbose_name = 'Currency Settings'

    def ready(self):
        """Initialize app"""
        pass
