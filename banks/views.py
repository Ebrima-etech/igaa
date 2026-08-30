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


class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Bank.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset


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
    filterset_fields = ['bank', 'status', 'submission_method', 'pilgrim']
    search_fields = ['reference_number', 'pilgrim_id', 'pilgrim__registration_id']
    ordering_fields = ['-submitted_at', 'amount', 'status']

    def get_queryset(self):
        user = self.request.user
        queryset = BankPaymentSubmission.objects.all()

        # Filter by bank if user is bank staff
        try:
            if hasattr(user, 'role') and user.role.role in ['bank_admin', 'bank_staff']:
                queryset = queryset.filter(bank=user.role.bank)
        except:
            pass

        # Filter by hajj_year if provided in query params
        hajj_year = self.request.query_params.get('hajj_year')
        if hajj_year:
            queryset = queryset.filter(pilgrim__hajj_year_id=hajj_year)

        return queryset

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
            # Get active Hajj year
            from dashboard.models import HajjYear
            active_hajj_year = HajjYear.objects.filter(is_active=True).first()

            # Step 1: Create the pilgrim directly with complete information
            pilgrim = Pilgrim.objects.create(
                first_name=serializer.validated_data['pilgrim_first_name'],
                last_name=serializer.validated_data['pilgrim_last_name'],
                gender=serializer.validated_data['pilgrim_gender'],
                phone=serializer.validated_data['pilgrim_phone'],
                email=serializer.validated_data.get('pilgrim_email') or None,
                date_of_birth=serializer.validated_data.get('pilgrim_date_of_birth'),
                nationality=serializer.validated_data.get('pilgrim_nationality', ''),
                passport_number=serializer.validated_data.get('pilgrim_passport_number', ''),
                address=serializer.validated_data.get('pilgrim_address', ''),
                city=serializer.validated_data.get('pilgrim_city', ''),
                state=serializer.validated_data.get('pilgrim_state', ''),
                postal_code=serializer.validated_data.get('pilgrim_postal_code', ''),
                country=serializer.validated_data.get('pilgrim_country', ''),
                hajj_year=active_hajj_year,  # Link to active Hajj year
            )

            # Step 2: Create the bank payment submission
            submission = BankPaymentSubmission.objects.create(
                bank=bank,
                pilgrim_id=pilgrim.id,
                amount=serializer.validated_data['amount'],
                reference_number=serializer.validated_data['reference_number'],
                payment_date=serializer.validated_data['payment_date'],
                description=serializer.validated_data.get('description', ''),
                submission_method='manual_form',
                submitted_by_user=user.username,
                status='verified',  # Mark as verified since pilgrim was just created
                # Store pilgrim information for reference
                pilgrim_first_name=pilgrim.first_name,
                pilgrim_last_name=pilgrim.last_name,
                pilgrim_gender=pilgrim.gender,
                pilgrim_phone=pilgrim.phone,
                pilgrim_email=pilgrim.email or '',
                # Store payer information
                payer_name=serializer.validated_data['payer_name'],
                payer_contact=serializer.validated_data.get('payer_contact', ''),
                payer_relationship=serializer.validated_data.get('payer_relationship', ''),
            )

            # Step 3: Payment will be created automatically via signal when submission is saved
            result_serializer = BankPaymentSubmissionSerializer(submission)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': f'Failed to create pilgrim or submission: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def current_submission(self, request):
        """Submit payment for existing pilgrim (current deposit)"""
        user = request.user
        bank = user.role.bank if hasattr(user, 'role') else None

        if not bank:
            return Response(
                {'error': 'User is not associated with a bank'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Extract required fields
        pilgrim_id = request.data.get('pilgrim_id')
        amount = request.data.get('amount')
        reference_number = request.data.get('reference_number')
        payment_date = request.data.get('payment_date')
        description = request.data.get('description', '')
        payer_name = request.data.get('payer_name')
        payer_contact = request.data.get('payer_contact', '')
        payer_relationship = request.data.get('payer_relationship', '')

        # Validate required fields
        if not all([pilgrim_id, amount, reference_number, payment_date, payer_name]):
            return Response(
                {'error': 'Missing required fields: pilgrim_id, amount, reference_number, payment_date, payer_name'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get existing pilgrim
            pilgrim = Pilgrim.objects.get(registration_id=pilgrim_id)

            # Create bank payment submission for existing pilgrim
            submission = BankPaymentSubmission.objects.create(
                bank=bank,
                pilgrim_id=pilgrim.id,
                amount=float(amount),
                reference_number=reference_number,
                payment_date=payment_date,
                description=description,
                submission_method='manual_form',
                submitted_by_user=user.username,
                status='verified',
                # Store pilgrim information for reference
                pilgrim_first_name=pilgrim.first_name,
                pilgrim_last_name=pilgrim.last_name,
                pilgrim_gender=pilgrim.gender,
                pilgrim_phone=pilgrim.phone,
                pilgrim_email=pilgrim.email or '',
                # Store payer information
                payer_name=payer_name,
                payer_contact=payer_contact,
                payer_relationship=payer_relationship,
            )

            result_serializer = BankPaymentSubmissionSerializer(submission)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        except Pilgrim.DoesNotExist:
            return Response(
                {'error': f'Pilgrim with ID {pilgrim_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create submission: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
