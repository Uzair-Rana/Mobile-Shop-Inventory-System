from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import RepairJob, RepairStatusLog, RepairPart
from .serializers import RepairJobSerializer, RepairStatusLogSerializer, RepairPartSerializer


class RepairJobViewSet(viewsets.ModelViewSet):
    queryset = RepairJob.objects.select_related(
        'customer', 'technician', 'branch', 'created_by'
    ).prefetch_related('logs', 'parts').all()
    serializer_class = RepairJobSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'branch', 'technician']
    search_fields = ['job_number', 'customer_name', 'device_model', 'device_imei']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        branch_id = self.request.headers.get('X-Branch-ID')
        if branch_id:
            qs = qs.filter(branch_id=branch_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='update_status')
    def update_status(self, request, pk=None):
        job = self.get_object()
        new_status = request.data.get('status')
        note = request.data.get('note', '')

        valid_statuses = [s[0] for s in RepairJob.STATUS]
        if new_status not in valid_statuses:
            return Response(
                {'detail': f'Invalid status. Choose from: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = job.status
        job.status = new_status
        job.save()

        RepairStatusLog.objects.create(
            repair=job,
            status=new_status,
            note=note or f'Status changed from {old_status} to {new_status}',
            actor=request.user,
        )
        return Response(RepairJobSerializer(job).data)

    @action(detail=True, methods=['post'], url_path='deliver')
    def deliver(self, request, pk=None):
        job = self.get_object()
        if job.status not in ('ready', 'repaired'):
            return Response(
                {'detail': 'Job must be in "ready" or "repaired" state to deliver.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        amount = request.data.get('amount_paid', 0)
        job.status = 'delivered'
        job.amount_paid = amount
        job.save()

        RepairStatusLog.objects.create(
            repair=job,
            status='delivered',
            note=request.data.get('note', 'Device delivered to customer.'),
            actor=request.user,
        )
        return Response(RepairJobSerializer(job).data)

    @action(detail=False, methods=['get'], url_path='board')
    def board(self, request):
        """Return all non-delivered jobs grouped by stage for the kanban board."""
        branch_id = request.headers.get('X-Branch-ID')
        qs = RepairJob.objects.exclude(status__in=['delivered', 'cancelled'])
        if branch_id:
            qs = qs.filter(branch_id=branch_id)

        stages = [s[0] for s in RepairJob.STATUS if s[0] not in ('delivered', 'cancelled')]
        board = {stage: [] for stage in stages}

        for job in qs.select_related('customer', 'technician', 'branch'):
            if job.status in board:
                board[job.status].append(RepairJobSerializer(job).data)

        return Response(board)
