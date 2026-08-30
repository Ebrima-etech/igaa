from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging
from .models import Pilgrim, PilgrimDocument
from .serializers import PilgrimSerializer, PilgrimListSerializer, PilgrimDocumentSerializer

logger = logging.getLogger(__name__)


class PilgrimViewSet(viewsets.ModelViewSet):
    queryset = Pilgrim.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'gender', 'nationality', 'hajj_year']
    search_fields = ['registration_id', 'first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['-created_at', 'first_name', 'status']

    def get_queryset(self):
        queryset = Pilgrim.objects.all()

        # Filter by hajj_year if provided in query params
        hajj_year = self.request.query_params.get('hajj_year')
        if hajj_year:
            queryset = queryset.filter(hajj_year_id=hajj_year)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return PilgrimListSerializer
        return PilgrimSerializer

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Pilgrim create request data: {request.data}")
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error creating pilgrim: {type(e).__name__}: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Failed to create pilgrim: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        pilgrims = Pilgrim.objects.filter(
            registration_id__icontains=query
        ) | Pilgrim.objects.filter(
            first_name__icontains=query
        ) | Pilgrim.objects.filter(
            last_name__icontains=query
        )
        serializer = PilgrimListSerializer(pilgrims[:20], many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        pilgrim = self.get_object()
        file = request.FILES.get('file')
        doc_type = request.data.get('document_type')

        if not file or not doc_type:
            return Response(
                {'error': 'file and document_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        doc = PilgrimDocument.objects.create(
            pilgrim=pilgrim,
            document_type=doc_type,
            document_file=file
        )
        serializer = PilgrimDocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def payment_history(self, request, pk=None):
        pilgrim = self.get_object()
        payments = pilgrim.payments.all()
        from payment.serializers import PaymentListSerializer
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)


class PilgrimDocumentViewSet(viewsets.ModelViewSet):
    queryset = PilgrimDocument.objects.all()
    serializer_class = PilgrimDocumentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['pilgrim', 'document_type']
