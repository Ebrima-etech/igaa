from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BankViewSet, BankAccountViewSet, BankPaymentSubmissionViewSet, PaymentMethodViewSet
)

router = DefaultRouter()
router.register(r'banks', BankViewSet, basename='bank')
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
router.register(r'bank-payment-submissions', BankPaymentSubmissionViewSet, basename='bank-payment-submission')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')

urlpatterns = [
    path('', include(router.urls)),
]
