from django.db import models


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

    registration_id = models.CharField(max_length=20, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', db_index=True)
    total_amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_email = models.EmailField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        return self.total_amount_due - self.total_amount_paid


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
