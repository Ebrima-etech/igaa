from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Q
import logging
from .models import Payment, PaymentSynchronization, Transaction, Receipt
from .serializers import PaymentSerializer, PaymentListSerializer, TransactionSerializer, ReceiptSerializer, ReceiptListSerializer

logger = logging.getLogger(__name__)


class IsStaffUser(IsAdminUser):
    """Permission class for staff users"""
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'bank', 'pilgrim']
    search_fields = ['reference_number', 'pilgrim__email', 'pilgrim__registration_id']
    ordering_fields = ['-created_at', 'amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Payment.objects.all()

        # Filter by bank if user is bank staff
        user = self.request.user
        try:
            role = user.role
            if role.role in ['bank_admin', 'bank_staff']:
                queryset = queryset.filter(bank=role.bank)
        except:
            pass

        # Filter by hajj_year if provided in query params
        hajj_year = self.request.query_params.get('hajj_year')
        if hajj_year:
            queryset = queryset.filter(pilgrim__hajj_year_id=hajj_year)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        payments = self.get_queryset()
        total_payments = payments.count()
        total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        confirmed = payments.filter(status='confirmed').count()
        pending = payments.filter(status='pending').count()

        return Response({
            'total_payments': total_payments,
            'total_amount': str(total_amount),
            'confirmed_count': confirmed,
            'pending_count': pending,
        })

    @action(detail=False, methods=['get'])
    def by_bank(self, request):
        from banks.models import Bank
        payments = self.get_queryset()
        banks = Bank.objects.filter(payments__in=payments).distinct()

        data = []
        for bank in banks:
            bank_payments = payments.filter(bank=bank)
            data.append({
                'bank': bank.name,
                'total_payments': bank_payments.count(),
                'total_amount': str(bank_payments.aggregate(Sum('amount'))['amount__sum'] or 0),
            })
        return Response(data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        payments = self.get_queryset()
        statuses = payments.values('status').distinct()

        data = []
        for status_item in statuses:
            status_val = status_item['status']
            count = payments.filter(status=status_val).count()
            amount = payments.filter(status=status_val).aggregate(Sum('amount'))['amount__sum'] or 0
            data.append({
                'status': status_val,
                'count': count,
                'amount': str(amount),
            })
        return Response(data)



class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['action', 'payment']
    ordering_fields = ['-created_at']


class ReceiptViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['signatory']
    search_fields = ['receipt_number', 'payment_reference']
    ordering_fields = ['-created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Receipt.objects.all()

        # Filter by created date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ReceiptListSerializer
        return ReceiptSerializer

    def create(self, request, *args, **kwargs):
        try:
            from settings_app.models import Signatory

            data = request.data.copy()
            receipt_number = data.get('receipt_number')

            # Check if receipt already exists
            if Receipt.objects.filter(receipt_number=receipt_number).exists():
                return Response(
                    {'detail': 'Receipt with this number already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Auto-fetch active signatory if not provided
            signatory_id = data.get('signatory')
            if not signatory_id or signatory_id == 0 or signatory_id == "0":
                try:
                    active_signatory = Signatory.objects.filter(is_active=True).first()
                    if not active_signatory:
                        # Fallback to any signatory if no active one
                        active_signatory = Signatory.objects.first()

                    if active_signatory:
                        data['signatory'] = active_signatory.id
                        logger.info(f'Auto-fetched active signatory: {active_signatory.signatory_name}')
                    else:
                        logger.warning('No signatory found in database')
                        data['signatory'] = None
                except Exception as e:
                    logger.warning(f'Error fetching signatory: {str(e)}')
                    data['signatory'] = None

            serializer = self.get_serializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f'Error creating receipt: {str(e)}')
            return Response(
                {'detail': f'Error creating receipt: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset()
        total_receipts = queryset.count()

        return Response({
            'total_receipts': total_receipts,
        })
