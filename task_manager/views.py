from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from django.db.models import Count, Q
from .models import Task
from .serializers import TaskModelSerializer

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskModelSerializer

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        total_tasks = Task.objects.count()

        status_counts = Task.objects.values('status').annotate(count=Count('id'))
        overdue_tasks = Task.objects.filter(
            Q(deadline__lt=now().date()) & ~Q(status='done')
        ).count()

        status_summary = {item['status']: item['count'] for item in status_counts}

        return Response({
            'total_tasks': total_tasks,
            'status_counts': status_summary,
            'overdue_tasks': overdue_tasks
        }, status=status.HTTP_200_OK)