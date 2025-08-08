from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import get_object_or_404, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import action
from django.db.models.functions import ExtractWeekDay
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .permissions import IsOwnerOrReadOnly
from .models import Task, SubTask, Category
from .serializers import SubTaskCreateSerializer, CategoryCreateSerializer, TaskModelSerializer, TaskDetailSerializer
from .paginator import SubTaskPagination, DefaultCursorPagination

from django.utils.timezone import now
from django.db.models import Count, Q


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskModelSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)  # owner ставится здесь

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskModelSerializer

    @action(detail=False, methods=['get'], url_path='stats', permission_classes=[IsAuthenticated])
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


class SubTaskListCreateView(ListCreateAPIView):
    queryset = SubTask.objects.all().order_by('-created_at')
    serializer_class = SubTaskCreateSerializer
    pagination_class = SubTaskPagination
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SubTaskDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskCreateSerializer
    permission_classes = [IsOwnerOrReadOnly]


class TaskListByDay(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultCursorPagination

    def get(self, request, *args, **kwargs):
        day_of_week = request.GET.get('day')

        if day_of_week:
            day_index = {
                'Monday': 2,
                'Tuesday': 3,
                'Wednesday': 4,
                'Thursday': 5,
                'Friday': 6,
                'Saturday': 7,
                'Sunday': 1,
            }

            weekday_num = day_index.get(day_of_week.capitalize())
            if weekday_num is None:
                return Response({'error': 'Invalid day name'}, status=status.HTTP_400_BAD_REQUEST)

            tasks = Task.objects.annotate(weekday=ExtractWeekDay('deadline')).filter(weekday=weekday_num)
        else:
            tasks = Task.objects.all()

        paginator = self.pagination_class
        page = paginator.paginate_queryset(tasks, request)
        serializer = TaskModelSerializer(tasks, many=True)
        return paginator.get_paginated_response(serializer.data)

class FilteredSubTaskListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultCursorPagination

    def get(self, request, *args, **kwargs):
        task_title = request.GET.get('task_title')
        status_param = request.GET.get('status')
        subtasks = SubTask.objects.select_related('task').order_by('-created_at')

        if task_title:
            subtasks = subtasks.filter(task__title__icontains=task_title)
        if status_param:
            subtasks = subtasks.filter(status=status_param)

        paginator = SubTaskPagination()
        page = paginator.paginate_queryset(subtasks, request)

        if page is not None:
            serializer = SubTaskCreateSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SubTaskCreateSerializer(subtasks, many=True)
        return paginator.get_paginated_response(serializer.data)


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='stats', permission_classes=[IsAuthenticated])
    def count_tasks(self, request):

        categories = Category.objects.annotate(task_count=Count('tasks'))
        data = [
            {"id": cat.id, "name": cat.name, "task_count": cat.task_count}
            for cat in categories
        ]
        return Response(data)