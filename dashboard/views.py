from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import DashboardReport, OperationalMetric
from .serializers import DashboardReportSerializer, OperationalMetricSerializer
from pilgrim.models import Pilgrim
from payment.models import Payment
from banks.models import Bank, BankPaymentSubmission


class DashboardReportViewSet(viewsets.ModelViewSet):
    queryset = DashboardReport.objects.all()
    serializer_class = DashboardReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['report_type']


class OperationalMetricViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OperationalMetric.objects.all()
    serializer_class = OperationalMetricSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['metric_type']


class DashboardSummaryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        try:
            role = request.user.role
            is_bank_user = role.role in ['bank_admin', 'bank_staff']
            bank = role.bank if is_bank_user else None
        except:
            is_bank_user = False
            bank = None

        if is_bank_user:
            payments = Payment.objects.filter(bank=bank)
            submissions = BankPaymentSubmission.objects.filter(bank=bank)
        else:
            payments = Payment.objects.all()
            submissions = BankPaymentSubmission.objects.all()

        total_pilgrims = Pilgrim.objects.count()
        total_paid = payments.filter(status='confirmed').aggregate(Sum('amount'))['amount__sum'] or 0
        total_pending = payments.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
        confirmed_count = payments.filter(status='confirmed').count()
        pending_count = payments.filter(status='pending').count()

        today_payments = payments.filter(
            created_at__date=timezone.now().date()
        ).count()

        return Response({
            'total_pilgrims': total_pilgrims,
            'total_paid': str(total_paid),
            'total_pending': str(total_pending),
            'confirmed_payments': confirmed_count,
            'pending_payments': pending_count,
            'payments_today': today_payments,
            'total_banks': Bank.objects.filter(is_active=True).count() if not is_bank_user else 1,
        })

    @action(detail=False, methods=['get'])
    def payment_by_status(self, request):
        try:
            role = request.user.role
            is_bank_user = role.role in ['bank_admin', 'bank_staff']
            bank = role.bank if is_bank_user else None
        except:
            is_bank_user = False
            bank = None

        if is_bank_user:
            payments = Payment.objects.filter(bank=bank)
        else:
            payments = Payment.objects.all()

        status_data = payments.values('status').annotate(
            count=Count('id'),
            amount=Sum('amount')
        )

        return Response([{
            'status': item['status'],
            'count': item['count'],
            'amount': str(item['amount'] or 0)
        } for item in status_data])

    @action(detail=False, methods=['get'])
    def payment_by_bank(self, request):
        try:
            role = request.user.role
            if role.role in ['bank_admin', 'bank_staff']:
                return Response({'error': 'Bank users cannot view other banks'}, status=status.HTTP_403_FORBIDDEN)
        except:
            pass

        bank_data = Payment.objects.values('bank__name').annotate(
            count=Count('id'),
            amount=Sum('amount')
        )

        return Response([{
            'bank': item['bank__name'],
            'count': item['count'],
            'amount': str(item['amount'] or 0)
        } for item in bank_data])

    @action(detail=False, methods=['get'])
    def recent_activity(self, request):
        try:
            role = request.user.role
            is_bank_user = role.role in ['bank_admin', 'bank_staff']
            bank = role.bank if is_bank_user else None
        except:
            is_bank_user = False
            bank = None

        if is_bank_user:
            submissions = BankPaymentSubmission.objects.filter(bank=bank)[:20]
        else:
            submissions = BankPaymentSubmission.objects.all()[:20]

        from banks.serializers import BankPaymentSubmissionSerializer
        serializer = BankPaymentSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)
