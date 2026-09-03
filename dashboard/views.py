from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import DashboardReport, OperationalMetric, HajjYear, Notification, ChatMessage, ChatGroup, GroupMessage
from .serializers import DashboardReportSerializer, OperationalMetricSerializer, HajjYearSerializer, NotificationSerializer, ChatMessageSerializer, ChatGroupSerializer, GroupMessageSerializer, UserSerializer
from django.contrib.auth.models import User
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
        """Return all Hajj years for staff, only active for non-staff"""
        queryset = HajjYear.objects.all()
        try:
            if not self.request.user.is_staff:
                queryset = queryset.filter(is_active=True)
        except:
            pass
        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new Hajj year - staff only"""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only staff members can create Hajj years'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update Hajj year - staff only"""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only staff members can update Hajj years'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Partial update Hajj year - staff only"""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Only staff members can update Hajj years'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

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

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Comprehensive analytics data for frontend"""
        hajj_year = request.query_params.get('hajj_year')

        # Build queries based on hajj_year
        if hajj_year:
            pilgrims = Pilgrim.objects.filter(hajj_year_id=hajj_year)
            submissions = BankPaymentSubmission.objects.filter(pilgrim__hajj_year_id=hajj_year)
        else:
            pilgrims = Pilgrim.objects.all()
            submissions = BankPaymentSubmission.objects.all()

        # 1. Pilgrim Trend - by registration date
        pilgrim_trend = {}
        for p in pilgrims:
            date_key = p.created_at.strftime('%Y-%m-%d')
            if date_key not in pilgrim_trend:
                pilgrim_trend[date_key] = {'registrations': 0, 'completed': 0, 'date': p.created_at.strftime('%b %d')}
            pilgrim_trend[date_key]['registrations'] += 1
            if p.amount_remaining == 0:
                pilgrim_trend[date_key]['completed'] += 1

        pilgrim_trend_list = sorted(pilgrim_trend.items(), key=lambda x: x[0])[-15:]
        pilgrim_trend_data = [{'date': v['date'], **v} for k, v in pilgrim_trend_list]

        # 2. Payment Trend - by payment date
        payment_trend = {}
        for s in submissions:
            date_key = s.payment_date.strftime('%Y-%m-%d')
            if date_key not in payment_trend:
                payment_trend[date_key] = {'amount': 0, 'transactions': 0, 'date': s.payment_date.strftime('%b %d')}
            payment_trend[date_key]['amount'] += float(s.amount)
            payment_trend[date_key]['transactions'] += 1

        payment_trend_list = sorted(payment_trend.items(), key=lambda x: x[0])[-15:]
        payment_trend_data = [{'date': v['date'], **v} for k, v in payment_trend_list]

        # 3. Age Distribution - from pilgrim date_of_birth
        age_ranges = {'18-25': 0, '26-35': 0, '36-45': 0, '46-55': 0, '56-65': 0, '65+': 0}
        today = datetime.now().date()
        for p in pilgrims:
            if p.date_of_birth:
                age = (today.year - p.date_of_birth.year) - ((today.month, today.day) < (p.date_of_birth.month, p.date_of_birth.day))
                if 18 <= age <= 25:
                    age_ranges['18-25'] += 1
                elif 26 <= age <= 35:
                    age_ranges['26-35'] += 1
                elif 36 <= age <= 45:
                    age_ranges['36-45'] += 1
                elif 46 <= age <= 55:
                    age_ranges['46-55'] += 1
                elif 56 <= age <= 65:
                    age_ranges['56-65'] += 1
                elif age > 65:
                    age_ranges['65+'] += 1

        age_distribution_data = [{'range': k, 'count': v} for k, v in age_ranges.items()]

        # 4. Region Distribution - from pilgrim region
        region_dist = {}
        region_choices = dict(Pilgrim.REGION_CHOICES)
        for p in pilgrims:
            region = p.region if p.region else 'Unknown'
            region_name = region_choices.get(region, region)
            region_dist[region_name] = region_dist.get(region_name, 0) + 1

        region_distribution_data = sorted([{'name': k, 'value': v} for k, v in region_dist.items()], key=lambda x: x['value'], reverse=True)

        # 5. Payment by Bank - from submissions
        bank_dist = {}
        for s in submissions:
            bank_name = s.bank.name
            bank_dist[bank_name] = bank_dist.get(bank_name, 0) + 1

        bank_distribution_data = sorted([{'name': k, 'value': v} for k, v in bank_dist.items()], key=lambda x: x['value'], reverse=True)

        # 6. Payment Status - Completed vs Uncompleted
        # Note: amount_remaining is a property, so we calculate it in Python, not in database query
        completed_count = 0
        uncompleted_count = 0
        for p in pilgrims:
            if p.amount_remaining == 0:
                completed_count += 1
            else:
                uncompleted_count += 1

        payment_status_data = [
            {'name': 'Completed', 'value': completed_count, 'color': '#22c55e'},
            {'name': 'Uncompleted', 'value': uncompleted_count, 'color': '#eab308'},
        ]

        # 7. Metrics
        total_pilgrims = pilgrims.count()
        total_payment_amount = submissions.aggregate(Sum('amount'))['amount__sum'] or 0
        payment_completion_rate = (completed_count / total_pilgrims * 100) if total_pilgrims > 0 else 0
        active_banks = Bank.objects.filter(is_active=True, submissions__isnull=False).distinct().count() if not hajj_year else Bank.objects.filter(is_active=True, submissions__pilgrim__hajj_year_id=hajj_year).distinct().count()
        total_regions = Pilgrim.objects.filter(**{'hajj_year_id': hajj_year} if hajj_year else {}).values_list('region', flat=True).distinct().count()

        metrics = {
            'totalPilgrims': total_pilgrims,
            'totalPayment': float(total_payment_amount),
            'avgPaymentAmount': float(total_payment_amount / submissions.count()) if submissions.count() > 0 else 0,
            'paymentCompletionRate': round(payment_completion_rate),
            'activeBanks': active_banks,
            'totalRegions': total_regions,
        }

        return Response({
            'pilgrimTrend': pilgrim_trend_data,
            'paymentTrend': payment_trend_data,
            'ageDistribution': age_distribution_data,
            'regionDistribution': region_distribution_data,
            'bankDistribution': bank_distribution_data,
            'paymentStatus': payment_status_data,
            'metrics': metrics,
        })


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['patch'])
    def mark_all_as_read(self, request):
        Notification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({'status': 'All notifications marked as read'})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, read=False).count()
        return Response({'unread_count': count})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def staff_list(self, request):
        users = User.objects.all()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


