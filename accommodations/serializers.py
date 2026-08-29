from rest_framework import serializers
from .models import Hotel, Room, RoomAssignment, RoomAssignmentBatch, Airport, Flight, FlightAssignment, FlightBatch
from pilgrim.models import Pilgrim


class HotelSerializer(serializers.ModelSerializer):
    rooms_count = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = ['id', 'name', 'location', 'city', 'country', 'phone', 'email', 'total_rooms', 'rooms_count', 'status', 'notes', 'created_at']
        read_only_fields = ['created_at']

    def get_rooms_count(self, obj):
        return obj.rooms.count()


class RoomSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    current_occupants_count = serializers.SerializerMethodField()
    available_beds = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'hotel', 'hotel_name', 'room_number', 'room_type', 'capacity', 'gender', 'floor_number', 'status', 'amenities', 'notes', 'current_occupants_count', 'available_beds', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_current_occupants_count(self, obj):
        return obj.get_current_occupants().count()

    def get_available_beds(self, obj):
        return obj.get_available_beds()


class RoomAssignmentSerializer(serializers.ModelSerializer):
    pilgrim_name = serializers.CharField(source='pilgrim.get_full_name', read_only=True)
    pilgrim_gender = serializers.CharField(source='pilgrim.gender', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    hotel_name = serializers.CharField(source='room.hotel.name', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = RoomAssignment
        fields = ['id', 'room', 'pilgrim', 'pilgrim_name', 'pilgrim_gender', 'room_number', 'hotel_name', 'check_in_date', 'check_out_date', 'days_stay', 'status', 'notes', 'assigned_by', 'assigned_by_username', 'assigned_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'assigned_at']


class RoomAssignmentBatchSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source='hotel.name', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)
    assignments_count = serializers.SerializerMethodField()

    class Meta:
        model = RoomAssignmentBatch
        fields = ['id', 'batch_name', 'hotel', 'hotel_name', 'check_in_date', 'check_out_date', 'days_stay', 'total_rooms_used', 'total_pilgrims', 'assignments_count', 'gender_segregation', 'people_per_room', 'status', 'assigned_by', 'assigned_by_username', 'assigned_at', 'confirmed_at', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'assigned_at', 'confirmed_at']

    def get_assignments_count(self, obj):
        # Count assignments related to this batch
        # This would need a way to link assignments to batches
        return 0


class PilgrimMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pilgrim
        fields = ['id', 'first_name', 'last_name', 'gender', 'phone', 'email', 'status']


# Flight Serializers

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ['id', 'code', 'name', 'city', 'country', 'created_at']
        read_only_fields = ['created_at']


class FlightSerializer(serializers.ModelSerializer):
    departure_airport_code = serializers.CharField(source='departure_airport.code', read_only=True)
    arrival_airport_code = serializers.CharField(source='arrival_airport.code', read_only=True)
    assigned_count = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = ['id', 'flight_number', 'airline', 'departure_airport', 'arrival_airport', 'departure_airport_code', 'arrival_airport_code', 'departure_date', 'arrival_date', 'departure_time', 'arrival_time', 'aircraft_type', 'total_capacity', 'assigned_count', 'available_seats', 'status', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_assigned_count(self, obj):
        return obj.get_assigned_count()

    def get_available_seats(self, obj):
        return obj.get_available_seats()


class FlightAssignmentSerializer(serializers.ModelSerializer):
    pilgrim_name = serializers.CharField(source='pilgrim.get_full_name', read_only=True)
    pilgrim_gender = serializers.CharField(source='pilgrim.gender', read_only=True)
    flight_number = serializers.CharField(source='flight.flight_number', read_only=True)
    departure_date = serializers.DateField(source='flight.departure_date', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = FlightAssignment
        fields = ['id', 'flight', 'pilgrim', 'pilgrim_name', 'pilgrim_gender', 'flight_number', 'departure_date', 'seat_number', 'boarding_group', 'special_requirements', 'status', 'notes', 'assigned_by', 'assigned_by_username', 'assigned_at', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'assigned_at']


class FlightBatchSerializer(serializers.ModelSerializer):
    departure_airport_code = serializers.CharField(source='departure_airport.code', read_only=True)
    arrival_airport_code = serializers.CharField(source='arrival_airport.code', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = FlightBatch
        fields = ['id', 'batch_name', 'departure_airport', 'arrival_airport', 'departure_airport_code', 'arrival_airport_code', 'departure_date', 'people_per_flight', 'total_flights', 'total_pilgrims', 'assignment_priority', 'status', 'assigned_by', 'assigned_by_username', 'assigned_at', 'confirmed_at', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'assigned_at', 'confirmed_at']
