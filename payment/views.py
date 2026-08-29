from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from .models import Payment, PaymentSynchronization, Transaction
from .serializers import PaymentSerializer, PaymentListSerializer, TransactionSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'bank', 'pilgrim']
    search_fields = ['reference_number', 'pilgrim__email', 'pilgrim__registration_id']
    ordering_fields = ['-created_at', 'amount', 'status']

    def get_queryset(self):
        user = self.request.user
        print(f"DEBUG: User {user.username}, has_role: {hasattr(user, 'role')}")
        try:
            role = user.role
            print(f"DEBUG: User role: {role.role}, bank: {role.bank}")
            if role.role in ['bank_admin', 'bank_staff']:
                print(f"DEBUG: Filtering by bank {role.bank}")
                return Payment.objects.filter(bank=role.bank)
        except Exception as e:
            print(f"DEBUG: Exception in get_queryset: {e}")
            pass
        print(f"DEBUG: Returning all payments")
        return Payment.objects.all()

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

    @action(detail=False, methods=['post'])
    def link_pilgrim(self, request):
        reference_number = request.data.get('reference_number')
        pilgrim_id = request.data.get('pilgrim_id')

        if not reference_number or not pilgrim_id:
            return Response(
                {'error': 'reference_number and pilgrim_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.get(reference_number=reference_number)
            payment.pilgrim_id = pilgrim_id
            payment.save()
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response(
                {'error': f'Payment with reference_number {reference_number} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to link pilgrim: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['action', 'payment']
    ordering_fields = ['-created_at']
