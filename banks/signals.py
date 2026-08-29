from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BankPaymentSubmission
from payment.models import Payment


@receiver(post_save, sender=BankPaymentSubmission)
def create_payment_from_bank_submission(sender, instance, created, **kwargs):
    """
    Automatically create a Payment record in GIA when a bank submission is created.
    This allows GIA to see incoming payments immediately and create pilgrims for them.
    """
    if created and instance.status == 'verified':
        # Only create payment if submission is verified
        print(f"DEBUG: Creating Payment from BankPaymentSubmission {instance.reference_number}")

        # Check if payment already exists for this reference
        if Payment.objects.filter(reference_number=instance.reference_number).exists():
            print(f"DEBUG: Payment already exists for {instance.reference_number}")
            return

        try:
            payment = Payment.objects.create(
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
        except Exception as e:
            print(f"DEBUG: Failed to create Payment for {instance.reference_number}: {e}")
            # Store error in submission
            instance.error_message = f"Failed to create payment in GIA: {str(e)}"
            instance.status = 'failed'
            instance.save(update_fields=['error_message', 'status'])
