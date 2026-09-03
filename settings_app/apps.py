# settings_app/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class SettingsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_app'
    verbose_name = 'Currency Settings'

    def ready(self):
        """Initialize app and register signals"""
        logger.info('🚀 settings_app.ready() called')
        try:
            # Import signals to register @receiver decorators
            import settings_app.signals  # noqa: F401
            logger.info('✓ signals.py imported successfully')
        except Exception as e:
            logger.exception(f'✗ Failed to import signals: {e}')
