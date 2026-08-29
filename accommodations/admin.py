from django.contrib import admin
from .models import Hotel, Room, RoomAssignment, RoomAssignmentBatch, Airport, Flight, FlightAssignment, FlightBatch


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'total_rooms', 'status', 'created_at')
    list_filter = ('status', 'country', 'created_at')
    search_fields = ('name', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'hotel', 'room_type', 'capacity', 'gender', 'status', 'floor_number')
    list_filter = ('hotel', 'room_type', 'gender', 'status')
    search_fields = ('room_number', 'hotel__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RoomAssignment)
class RoomAssignmentAdmin(admin.ModelAdmin):
    list_display = ('pilgrim', 'room', 'check_in_date', 'check_out_date', 'days_stay', 'status')
    list_filter = ('status', 'check_in_date', 'room__hotel')
    search_fields = ('pilgrim__first_name', 'pilgrim__last_name', 'room__room_number')
    readonly_fields = ('created_at', 'updated_at', 'assigned_at')
    date_hierarchy = 'check_in_date'


@admin.register(RoomAssignmentBatch)
class RoomAssignmentBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_name', 'hotel', 'check_in_date', 'total_pilgrims', 'status', 'assigned_at')
    list_filter = ('status', 'hotel', 'check_in_date')
    search_fields = ('batch_name', 'hotel__name')
    readonly_fields = ('created_at', 'updated_at', 'assigned_at', 'confirmed_at')
    date_hierarchy = 'check_in_date'


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'city', 'country', 'created_at')
    list_filter = ('country', 'created_at')
    search_fields = ('code', 'name', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('flight_number', 'airline', 'departure_airport', 'arrival_airport', 'departure_date', 'total_capacity', 'status')
    list_filter = ('status', 'departure_date', 'aircraft_type', 'airline')
    search_fields = ('flight_number', 'airline')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'departure_date'


@admin.register(FlightAssignment)
class FlightAssignmentAdmin(admin.ModelAdmin):
    list_display = ('pilgrim', 'flight', 'seat_number', 'boarding_group', 'status', 'assigned_at')
    list_filter = ('status', 'flight__departure_date', 'boarding_group')
    search_fields = ('pilgrim__first_name', 'pilgrim__last_name', 'flight__flight_number', 'seat_number')
    readonly_fields = ('created_at', 'updated_at', 'assigned_at')
    date_hierarchy = 'flight__departure_date'


@admin.register(FlightBatch)
class FlightBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_name', 'departure_airport', 'arrival_airport', 'departure_date', 'total_pilgrims', 'status', 'assigned_at')
    list_filter = ('status', 'departure_airport', 'arrival_airport', 'departure_date')
    search_fields = ('batch_name', 'departure_airport__code', 'arrival_airport__code')
    readonly_fields = ('created_at', 'updated_at', 'assigned_at', 'confirmed_at')
    date_hierarchy = 'departure_date'
