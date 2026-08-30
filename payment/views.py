from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from .models import Payment, PaymentSynchronization, Transaction
from .serializers import PaymentSerializer, PaymentListSerializer, TransactionSerializer


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
