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


# Flight Assignment Models

class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True, db_index=True)  # e.g., "BXI", "JED"
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Flight(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('departed', 'Departed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    AIRCRAFT_CHOICES = [
        ('B777', 'Boeing 777'),
        ('B787', 'Boeing 787'),
        ('A380', 'Airbus A380'),
        ('A350', 'Airbus A350'),
        ('A320', 'Airbus A320'),
        ('B737', 'Boeing 737'),
    ]

    flight_number = models.CharField(max_length=20, unique=True, db_index=True)  # e.g., "GA101"
    airline = models.CharField(max_length=100)

    departure_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='departing_flights')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='arriving_flights')

    departure_date = models.DateField()
    arrival_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()

    aircraft_type = models.CharField(max_length=20, choices=AIRCRAFT_CHOICES)
    total_capacity = models.IntegerField(validators=[MinValueValidator(1)])

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-departure_date', 'flight_number']

    def __str__(self):
        return f"{self.flight_number} ({self.departure_airport.code} → {self.arrival_airport.code})"

    def get_assigned_count(self):
        """Get number of pilgrims assigned to this flight"""
        return FlightAssignment.objects.filter(flight=self, status__in=['assigned', 'checked_in', 'boarded']).count()

    def get_available_seats(self):
        """Get number of available seats"""
        assigned = self.get_assigned_count()
        return max(0, self.total_capacity - assigned)


class FlightAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('checked_in', 'Checked In'),
        ('boarded', 'Boarded'),
        ('cancelled', 'Cancelled'),
    ]

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='assignments')
    pilgrim = models.ForeignKey(Pilgrim, on_delete=models.CASCADE, related_name='flight_assignments')

    seat_number = models.CharField(max_length=10, blank=True, null=True)  # e.g., "12A", "1F"
    boarding_group = models.CharField(max_length=5, blank=True)  # e.g., "A", "B", "C"

    special_requirements = models.JSONField(default=list, blank=True)  # e.g., ["wheelchair", "elderly"]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')

    notes = models.TextField(blank=True)

    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='flight_assignments_created')
    assigned_at = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['flight__departure_date', 'boarding_group', 'seat_number']
        unique_together = ['flight', 'pilgrim']

    def __str__(self):
        return f"{self.pilgrim.first_name} {self.pilgrim.last_name} - {self.flight.flight_number}"


class FlightBatch(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ]

    batch_name = models.CharField(max_length=200)
    departure_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='departure_batches')
    arrival_airport = models.ForeignKey(Airport, on_delete=models.PROTECT, related_name='arrival_batches')

    departure_date = models.DateField()
    people_per_flight = models.IntegerField(validators=[MinValueValidator(1)], default=400)

    total_flights = models.IntegerField(validators=[MinValueValidator(0)])
    total_pilgrims = models.IntegerField(validators=[MinValueValidator(0)])

    assignment_priority = models.CharField(
        max_length=50,
        choices=[
            ('fifo', 'First In First Out'),
            ('family', 'Families Together'),
            ('age', 'Age Priority (Elderly First)'),
        ],
        default='fifo'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='flight_batches')
    assigned_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_at']
        verbose_name = 'Flight Batch'
        verbose_name_plural = 'Flight Batches'

    def __str__(self):
        return self.batch_name
