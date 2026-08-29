from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BankPaymentSubmission


@receiver(post_save, sender=BankPaymentSubmission)
def bank_submission_created(sender, instance, created, **kwargs):
    """
    Signal when BankPaymentSubmission is created.
    Payment will be created from GIA when admin creates the pilgrim.
    """
    if created:
        print(f"DEBUG: BankPaymentSubmission created: {instance.reference_number}")
        print(f"DEBUG: Pilgrim info: {instance.pilgrim_first_name} {instance.pilgrim_last_name}")
        print(f"DEBUG: Amount: {instance.amount} GMD")
        print(f"DEBUG: GIA will create Payment when pilgrim is created from this submission")
