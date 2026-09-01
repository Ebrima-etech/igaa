from weasyprint import HTML, CSS
from io import BytesIO
from django.template.loader import render_to_string
from django.utils.html import escape
import logging

logger = logging.getLogger(__name__)


def generate_receipt_pdf(receipt):
    """
    Generate a PDF receipt from a Receipt object.

    Args:
        receipt: Receipt model instance

    Returns:
        BytesIO object containing the PDF
    """
    try:
        # Prepare receipt data
        receipt_data = {
            'receipt_number': receipt.receipt_number,
            'pilgrim_first_name': escape(receipt.pilgrim_first_name or ''),
            'pilgrim_last_name': escape(receipt.pilgrim_last_name or ''),
            'pilgrim_email': escape(receipt.pilgrim_email or ''),
            'pilgrim_phone': escape(receipt.pilgrim_phone or ''),
            'pilgrim_passport': escape(receipt.pilgrim_passport or ''),
            'pilgrim_dob': receipt.pilgrim_dob or '',
            'pilgrim_gender': 'Male (Alagie)' if receipt.pilgrim_gender == 'M' else 'Female (Aja)',
            'payer_name': escape(receipt.payer_name or ''),
            'payer_relationship': escape(receipt.payer_relationship or ''),
            'amount': float(receipt.amount),
            'payment_date': receipt.payment_date,
            'generated_at': receipt.generated_at,
            'signatory_name': receipt.signatory.signatory_name if receipt.signatory else 'GIA Bank Admin',
            'signatory_title': receipt.signatory.signatory_title if receipt.signatory else 'Bank Administrator',
        }

        # Render HTML template
        html_content = render_to_string('receipt_pdf.html', receipt_data)

        # Generate PDF
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        pdf_file.seek(0)

        logger.info(f'Generated PDF for receipt {receipt.receipt_number}')
        return pdf_file

    except Exception as e:
        logger.exception(f'Error generating receipt PDF: {str(e)}')
        raise
