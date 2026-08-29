from django.contrib import admin
from .models import Hotel, Room, RoomAssignment, RoomAssignmentBatch


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
