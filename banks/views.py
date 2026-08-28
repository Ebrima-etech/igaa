from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import csv
import io
from .models import Bank, BankAccount, BankPaymentSubmission, PaymentMethod
from .serializers import (
    BankSerializer, BankAccountSerializer, BankPaymentSubmissionSerializer,
    PaymentMethodSerializer, ManualPaymentSubmissionSerializer, CSVPaymentUploadSerializer
)
from payment.models import Payment
from pilgrim.models import Pilgrim


class BankViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bank.objects.filter(is_active=True)
    serializer_class = BankSerializer
    permission_classes = [IsAuthenticated]


class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            if hasattr(user, 'role') and user.role.role in ['bank_admin', 'bank_staff']:
                return BankAccount.objects.filter(bank=user.role.bank)
        except:
            pass
        return BankAccount.objects.all()


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['bank', 'method_type', 'is_enabled']


class BankPaymentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = BankPaymentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['bank', 'status', 'submission_method']
    search_fields = ['reference_number', 'pilgrim_id']
    ordering_fields = ['-submitted_at']

    def get_queryset(self):
        user = self.request.user
        try:
            if hasattr(user, 'role') and user.role.role in ['bank_admin', 'bank_staff']:
                return BankPaymentSubmission.objects.filter(bank=user.role.bank)
        except:
            pass
        return BankPaymentSubmission.objects.all()

    @action(detail=False, methods=['post'])
    def manual_submission(self, request):
        serializer = ManualPaymentSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        bank = user.role.bank if hasattr(user, 'role') else None

        if not bank:
            return Response(
                {'error': 'User is not associated with a bank'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            pilgrim = Pilgrim.objects.get(registration_id=serializer.validated_data['pilgrim_id'])
        except Pilgrim.DoesNotExist:
            return Response(
                {'error': 'Pilgrim not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        submission = BankPaymentSubmission.objects.create(
            bank=bank,
            pilgrim_id=serializer.validated_data['pilgrim_id'],
            amount=serializer.validated_data['amount'],
            reference_number=serializer.validated_data['reference_number'],
            payment_date=serializer.validated_data['payment_date'],
            description=serializer.validated_data.get('description', ''),
            submission_method='manual_form',
            submitted_by_user=user.username,
            status='verified'
        )

        Payment.objects.create(
            pilgrim=pilgrim,
            bank=bank,
            amount=serializer.validated_data['amount'],
            reference_number=serializer.validated_data['reference_number'],
            payment_date=serializer.validated_data['payment_date'],
            status='confirmed'
        )

        result_serializer = BankPaymentSubmissionSerializer(submission)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        serializer = CSVPaymentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        bank = user.role.bank if hasattr(user, 'role') else None

        if not bank:
            return Response(
                {'error': 'User is not associated with a bank'},
                status=status.HTTP_403_FORBIDDEN
            )

        csv_file = serializer.validated_data['csv_file']
        results = []
        errors = []

        try:
            csv_reader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))

            for row_num, row in enumerate(csv_reader, 1):
                try:
                    pilgrim = Pilgrim.objects.get(registration_id=row['pilgrim_id'])

                    submission = BankPaymentSubmission.objects.create(
                        bank=bank,
                        pilgrim_id=row['pilgrim_id'],
                        amount=float(row['amount']),
                        reference_number=row['reference_number'],
                        payment_date=row['payment_date'],
                        description=row.get('description', ''),
                        submission_method='csv_upload',
                        submitted_by_user=user.username,
                        status='verified'
                    )

                    Payment.objects.create(
                        pilgrim=pilgrim,
                        bank=bank,
                        amount=float(row['amount']),
                        reference_number=row['reference_number'],
                        payment_date=row['payment_date'],
                        status='confirmed'
                    )

                    results.append({'row': row_num, 'reference_number': row['reference_number'], 'status': 'success'})
                except Exception as e:
                    errors.append({'row': row_num, 'error': str(e)})

        except Exception as e:
            return Response(
                {'error': f'CSV parsing error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'successful': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors
        }, status=status.HTTP_201_CREATED)
