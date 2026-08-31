# settings_app/urls.py
from django.urls import path
from .views import CurrencySettingsView, CurrencyRatesListView, HajjPackagePriceView

app_name = 'settings_app'

urlpatterns = [
    # Currency settings endpoints
    path(
        'settings/currency/',
        CurrencySettingsView.as_view(),
        name='currency-settings'
    ),
    path(
        'currency-rates/',
        CurrencyRatesListView.as_view(),
        name='currency-rates'
    ),
    # Hajj package price endpoint
    path(
        'settings/hajj-package-price/',
        HajjPackagePriceView.as_view(),
        name='hajj-package-price'
    ),
]
