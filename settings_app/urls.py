# settings_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CurrencySettingsView,
    CurrencyRatesListView,
    HajjPackagePriceView,
    SignatorySettingsView,
    SignatoryListView,
    SignatoryDetailView,
    EmailNotificationViewSet,
)

router = DefaultRouter()
router.register(r'settings/email-notifications', EmailNotificationViewSet, basename='email-notification')

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
    # Signatory endpoints
    path(
        'signatories/',
        SignatoryListView.as_view(),
        name='signatory-list'
    ),
    path(
        'signatories/<int:signatory_id>/',
        SignatoryDetailView.as_view(),
        name='signatory-detail'
    ),
    path(
        'signatories/active/',
        SignatoryDetailView.as_view(),
        name='signatory-active'
    ),
    # Global signatory settings
    path(
        'settings/signatory/',
        SignatorySettingsView.as_view(),
        name='signatory-settings'
    ),
]

# Add router URLs for email notifications
urlpatterns += router.urls
