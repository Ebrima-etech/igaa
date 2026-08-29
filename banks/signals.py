from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BankPaymentSubmission
from payment.models import Payment


@receiver(post_save, sender=BankPaymentSubmission)
def create_payment_from_bank_submission(sender, instance, created, **kwargs):
    """
    Automatically create a Payment record when bank submission is created.
    Payment has no pilgrim link yet - will be linked when GIA creates the pilgrim.
    """
    if created and instance.status == 'pending':
        print(f"DEBUG: Creating Payment from BankPaymentSubmission {instance.reference_number}")

        # Check if payment already exists
        if Payment.objects.filter(reference_number=instance.reference_number).exists():
            print(f"DEBUG: Payment already exists for {instance.reference_number}")
            return

        try:
            payment = Payment.objects.create(
                # No pilgrim yet - will be linked later
                pilgrim=None,
                bank=instance.bank,
                amount=instance.amount,
                reference_number=instance.reference_number,
                payment_date=instance.payment_date,
                description=instance.description or f"Bank submission from {instance.bank.name}",
                status='confirmed',
                # Payer information
                payer_name=instance.payer_name,
                payer_contact=instance.payer_contact,
                payer_relationship=instance.payer_relationship,
            )
            print(f"DEBUG: Successfully created Payment {payment.id} for {instance.reference_number}")
            print(f"DEBUG: Payment will be linked to pilgrim when created in GIA")
        except Exception as e:
            print(f"DEBUG: Failed to create Payment for {instance.reference_number}: {e}")
            instance.error_message = f"Failed to create payment: {str(e)}"
            instance.status = 'failed'
            instance.save(update_fields=['error_message', 'status'])
