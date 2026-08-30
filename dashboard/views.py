from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import DashboardReport, OperationalMetric, HajjYear
from .serializers import DashboardReportSerializer, OperationalMetricSerializer, HajjYearSerializer
from pilgrim.models import Pilgrim
from payment.models import Payment
from banks.models import Bank, BankPaymentSubmission


class HajjYearViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Hajj years"""
    queryset = HajjYear.objects.all()
    serializer_class = HajjYearSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-year']

    def get_queryset(self):
        """Non-admins can only view active Hajj years"""
        queryset = HajjYear.objects.all()
        try:
            if not self.request.user.is_staff:
                queryset = queryset.filter(is_active=True)
        except:
            pass
        return queryset

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active Hajj year"""
        active_hajj = HajjYear.objects.filter(is_active=True).first()
        if active_hajj:
            serializer = self.get_serializer(active_hajj)
            return Response(serializer.data)
        return Response({'error': 'No active Hajj year'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get statistics for all Hajj years"""
        hajj_years = self.get_queryset().order_by('-year')
        stats = []

        for year in hajj_years:
            pilgrims = Pilgrim.objects.filter(hajj_year=year)
            pilgrim_count = pilgrims.count()

            # Get payments for pilgrims in this year
            submissions = BankPaymentSubmission.objects.filter(
                pilgrim__in=pilgrims
            )

            verified_count = submissions.filter(status='verified').count()
            pending_count = submissions.filter(status='pending').count()
            total_payment = submissions.aggregate(Sum('amount'))['amount__sum'] or 0

            stats.append({
                'id': year.id,
                'year': year.year,
                'name': year.name,
                'pilgrims': pilgrim_count,
                'verified': verified_count,
                'pending': pending_count,
                'totalPayment': float(total_payment),
            })

        return Response(stats)


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
