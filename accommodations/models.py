from django.db import models
from django.core.validators import MinValueValidator
from pilgrim.models import Pilgrim
from users.models import User


class Hotel(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Maintenance'),
    ]

    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    total_rooms = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Hotel'
        verbose_name_plural = 'Hotels'

    def __str__(self):
        return self.name


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
        ('quad', 'Quad'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male Only'),
        ('F', 'Female Only'),
        ('Mixed', 'Mixed'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
        ('reserved', 'Reserved'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=50)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Mixed')

    floor_number = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    amenities = models.JSONField(default=list, blank=True, help_text='List of amenities (AC, WiFi, etc.)')
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['hotel', 'room_number']
        unique_together = ['hotel', 'room_number']

    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number}"

    def get_current_occupants(self):
        """Get current pilgrims assigned to this room"""
        return Pilgrim.objects.filter(
            roomassignment__room=self,
            roomassignment__status='active'
        ).distinct()

    def get_available_beds(self):
        """Get number of available beds in this room"""
        current_count = self.get_current_occupants().count()
        return max(0, self.capacity - current_count)


class RoomAssignment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='assignments')
    pilgrim = models.ForeignKey(Pilgrim, on_delete=models.CASCADE, related_name='room_assignments')

    check_in_date = models.DateField()
    check_out_date = models.DateField()
    days_stay = models.IntegerField(validators=[MinValueValidator(1)])

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)

    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='room_assignments_created')
    assigned_at = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-check_in_date', 'room__hotel']
        unique_together = ['room', 'pilgrim', 'check_in_date']

    def __str__(self):
        return f"{self.pilgrim.first_name} {self.pilgrim.last_name} - {self.room}"


class RoomAssignmentBatch(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ]

    batch_name = models.CharField(max_length=200)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='assignment_batches')

    check_in_date = models.DateField()
    check_out_date = models.DateField()
    days_stay = models.IntegerField(validators=[MinValueValidator(1)])

    total_rooms_used = models.IntegerField(validators=[MinValueValidator(0)])
    total_pilgrims = models.IntegerField(validators=[MinValueValidator(0)])

    gender_segregation = models.BooleanField(default=True)
    people_per_room = models.IntegerField(validators=[MinValueValidator(1)], default=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='room_assignment_batches')
    assigned_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_at']
        verbose_name = 'Room Assignment Batch'
        verbose_name_plural = 'Room Assignment Batches'

    def __str__(self):
        return self.batch_name
