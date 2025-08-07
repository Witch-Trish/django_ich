from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from django.db.models.functions import ExtractWeekDay

from .models import SubTask
from .serializers import SubTaskCreateSerializer
from .paginator import SubTaskPagination

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


class SubTaskListCreateView(APIView):
    def get(self, request, *args, **kwargs):
        subtasks = SubTask.objects.all().order_by('-created_at')
        paginator = SubTaskPagination()
        page = paginator.paginate_queryset(subtasks, request)
        if page is not None:
            serializer = SubTaskCreateSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = SubTaskCreateSerializer(subtasks, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubTaskDetailUpdateDeleteView(APIView):
    def get_object(self, pk):
        return get_object_or_404(SubTask, pk=pk)

    def get(self, request, pk, *args, **kwargs):
        subtask = self.get_object(pk)
        serializer = SubTaskCreateSerializer(subtask)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        subtask = self.get_object(pk)
        serializer = SubTaskCreateSerializer(subtask, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        subtask = self.get_object(pk)
        serializer = SubTaskCreateSerializer(subtask, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subtask = self.get_object(pk)
        subtask.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListByDay(APIView):
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

        serializer = TaskModelSerializer(tasks, many=True)
        return Response(serializer.data)

class FilteredSubTaskListView(APIView):
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

        # Если пагинация не нужна — вернуть все объекты
        serializer = SubTaskCreateSerializer(subtasks, many=True)
        return Response(serializer.data)