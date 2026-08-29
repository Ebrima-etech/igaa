from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Hotel, Room, RoomAssignment, RoomAssignmentBatch
from .serializers import HotelSerializer, RoomSerializer, RoomAssignmentSerializer, RoomAssignmentBatchSerializer, PilgrimMinimalSerializer
from pilgrim.models import Pilgrim


class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'country', 'city']
    search_fields = ['name', 'city', 'country']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['hotel', 'status', 'gender', 'room_type']
    search_fields = ['room_number', 'hotel__name']
    ordering_fields = ['hotel', 'room_number', 'capacity']
    ordering = ['hotel', 'room_number']

    @action(detail=False, methods=['get'])
    def available_rooms(self, request):
        """Get available rooms for assignment"""
        hotel_id = request.query_params.get('hotel_id')
        check_in_date = request.query_params.get('check_in_date')
        days_stay = request.query_params.get('days_stay', 1)
        capacity = request.query_params.get('capacity')
        gender = request.query_params.get('gender')

        rooms = self.get_queryset().filter(status='available')

        if hotel_id:
            rooms = rooms.filter(hotel_id=hotel_id)

        if capacity:
            rooms = rooms.filter(capacity__gte=capacity)

        if gender:
            rooms = rooms.filter(gender__in=[gender, 'Mixed'])

        # Check if rooms are available for the date range
        if check_in_date and days_stay:
            try:
                check_in = datetime.strptime(check_in_date, '%Y-%m-%d').date()
                check_out = check_in + timedelta(days=int(days_stay))

                # Exclude rooms with overlapping assignments
                occupied_room_ids = RoomAssignment.objects.filter(
                    status='active',
                    check_in_date__lt=check_out,
                    check_out_date__gt=check_in
                ).values_list('room_id', flat=True)

                rooms = rooms.exclude(id__in=occupied_room_ids)
            except ValueError:
                return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)


class RoomAssignmentViewSet(viewsets.ModelViewSet):
    queryset = RoomAssignment.objects.all()
    serializer_class = RoomAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['room__hotel', 'status', 'check_in_date', 'pilgrim']
    search_fields = ['pilgrim__first_name', 'pilgrim__last_name', 'room__room_number']
    ordering_fields = ['check_in_date', 'pilgrim__first_name']
    ordering = ['-check_in_date']

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    @action(detail=False, methods=['post'])
    def auto_assign(self, request):
        """Automatically assign pilgrims to rooms"""
        try:
            hotel_id = request.data.get('hotel_id')
            check_in_date_str = request.data.get('check_in_date')
            days_stay = int(request.data.get('days_stay', 1))
            people_per_room = int(request.data.get('people_per_room', 2))
            gender_segregation = request.data.get('gender_segregation', True)

            # Validate inputs
            if not all([hotel_id, check_in_date_str]):
                return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

            check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()
            check_out_date = check_in_date + timedelta(days=days_stay)

            hotel = Hotel.objects.get(id=hotel_id)

            # Get unassigned pilgrims
            assigned_pilgrim_ids = RoomAssignment.objects.filter(
                check_in_date__lte=check_out_date,
                check_out_date__gte=check_in_date,
                status='active'
            ).values_list('pilgrim_id', flat=True)

            unassigned_pilgrims = Pilgrim.objects.filter(status='paid').exclude(id__in=assigned_pilgrim_ids).order_by('gender', 'last_name')

            # Get available rooms
            occupied_room_ids = RoomAssignment.objects.filter(
                status='active',
                check_in_date__lt=check_out_date,
                check_out_date__gt=check_in_date
            ).values_list('room_id', flat=True)

            available_rooms = hotel.rooms.filter(
                status='available'
            ).exclude(id__in=occupied_room_ids).order_by('room_number')

            if not available_rooms.exists():
                return Response({'error': 'No available rooms in this hotel'}, status=status.HTTP_400_BAD_REQUEST)

            assignments = []
            rooms_used = 0
            current_room_idx = 0

            if gender_segregation:
                # Group by gender
                male_pilgrims = [p for p in unassigned_pilgrims if p.gender == 'M']
                female_pilgrims = [p for p in unassigned_pilgrims if p.gender == 'F']

                # Assign male pilgrims
                for pilgrims_group in [male_pilgrims, female_pilgrims]:
                    for i in range(0, len(pilgrims_group), people_per_room):
                        if current_room_idx >= available_rooms.count():
                            break

                        room = available_rooms[current_room_idx]
                        group = pilgrims_group[i:i+people_per_room]

                        for pilgrim in group:
                            assignment = RoomAssignment(
                                room=room,
                                pilgrim=pilgrim,
                                check_in_date=check_in_date,
                                check_out_date=check_out_date,
                                days_stay=days_stay,
                                assigned_by=request.user
                            )
                            assignments.append(assignment)

                        current_room_idx += 1
                        rooms_used += 1
            else:
                # No gender segregation, just fill rooms
                for i in range(0, len(unassigned_pilgrims), people_per_room):
                    if current_room_idx >= available_rooms.count():
                        break

                    room = available_rooms[current_room_idx]
                    group = unassigned_pilgrims[i:i+people_per_room]

                    for pilgrim in group:
                        assignment = RoomAssignment(
                            room=room,
                            pilgrim=pilgrim,
                            check_in_date=check_in_date,
                            check_out_date=check_out_date,
                            days_stay=days_stay,
                            assigned_by=request.user
                        )
                        assignments.append(assignment)

                    current_room_idx += 1
                    rooms_used += 1

            # Bulk create assignments
            RoomAssignment.objects.bulk_create(assignments)

            # Create batch record
            batch = RoomAssignmentBatch.objects.create(
                batch_name=f"{hotel.name} - {check_in_date.strftime('%Y-%m-%d')}",
                hotel=hotel,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                days_stay=days_stay,
                total_rooms_used=rooms_used,
                total_pilgrims=len(assignments),
                gender_segregation=gender_segregation,
                people_per_room=people_per_room,
                assigned_by=request.user,
                status='confirmed'
            )

            return Response({
                'success': True,
                'batch_id': batch.id,
                'total_assignments': len(assignments),
                'rooms_used': rooms_used,
                'assignments': RoomAssignmentSerializer(assignments, many=True).data
            }, status=status.HTTP_201_CREATED)

        except Hotel.DoesNotExist:
            return Response({'error': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoomAssignmentBatchViewSet(viewsets.ModelViewSet):
    queryset = RoomAssignmentBatch.objects.all()
    serializer_class = RoomAssignmentBatchSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['hotel', 'status', 'check_in_date']
    search_fields = ['batch_name', 'hotel__name']
    ordering_fields = ['check_in_date', 'assigned_at']
    ordering = ['-assigned_at']

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a batch assignment"""
        batch = self.get_object()
        if batch.status != 'draft':
            return Response({'error': 'Only draft batches can be confirmed'}, status=status.HTTP_400_BAD_REQUEST)

        batch.status = 'confirmed'
        batch.confirmed_at = timezone.now()
        batch.save()

        return Response({
            'success': True,
            'message': f'Batch {batch.batch_name} confirmed'
        })
