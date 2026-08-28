# settings_app/urls.py
from django.urls import path
from .views import CurrencySettingsView, CurrencyRatesListView

app_name = 'settings_app'

urlpatterns = [
    # Currency settings endpoints
    path(
        'api/v1/settings/currency/',
        CurrencySettingsView.as_view(),
        name='currency-settings'
    ),
    path(
        'api/v1/currency-rates/',
        CurrencyRatesListView.as_view(),
        name='currency-rates'
    ),
]
