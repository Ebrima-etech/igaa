from django.db import models
import uuid


class Pilgrim(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('paid', 'Paid'),
        ('departed', 'Departed'),
        ('returned', 'Returned'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    # Import HajjYear dynamically to avoid circular imports
    hajj_year = models.ForeignKey('dashboard.HajjYear', on_delete=models.PROTECT, null=True, blank=True, help_text="The Hajj year this pilgrim is registered for")

    registration_id = models.CharField(max_length=20, unique=True, db_index=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100, blank=True)
    passport_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', db_index=True)
    total_amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_email = models.EmailField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.registration_id:
            self.registration_id = self.generate_registration_id()

        # Calculate total_amount_due based on Hajj year package price
        if self.hajj_year and self.hajj_year.total_package_fee:
            self.total_amount_due = self.hajj_year.total_package_fee

        super().save(*args, **kwargs)

    @staticmethod
    def generate_registration_id():
        import time
        timestamp = int(time.time() * 1000) % 1000000
        return f"GH{timestamp:06d}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['registration_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.registration_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def amount_remaining(self):
        """Current due amount: package price - total paid"""
        package_price = self.total_amount_due
        if self.hajj_year and self.hajj_year.total_package_fee:
            package_price = self.hajj_year.total_package_fee
        return package_price - self.total_amount_paid

    @property
    def current_due(self):
        """Alias for amount_remaining - same calculation"""
        return self.amount_remaining


class PilgrimDocument(models.Model):
    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('visa', 'Visa'),
        ('id_card', 'ID Card'),
        ('medical', 'Medical Certificate'),
        ('insurance', 'Insurance Document'),
        ('other', 'Other'),
    ]

    pilgrim = models.ForeignKey(Pilgrim, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='pilgrim_documents/%Y/%m/%d/')
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.pilgrim.full_name} - {self.get_document_type_display()}"
