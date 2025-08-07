from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, SubTaskListCreateView, SubTaskDetailUpdateDeleteView, TaskListByDay, \
    FilteredSubTaskListView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:pk>/', SubTaskDetailUpdateDeleteView.as_view(), name='subtask-detail-update'),
    path('subtasks/filter/', FilteredSubTaskListView.as_view(), name='subtask-list-filter'),
    path('tasks-by-day/', TaskListByDay.as_view(), name='task-list-by-day'),

]