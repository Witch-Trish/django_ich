from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'task_manager_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_category_name')
        ]


class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In progress'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=255, verbose_name="Task Title", unique=True )
    description = models.TextField(blank=True, verbose_name="Task Description")
    categories = models.ManyToManyField(Category, related_name='tasks', verbose_name="Task Categories")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Task Status")
    deadline = models.DateTimeField(verbose_name="Deadline")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        db_table = 'task_manager_task'
        ordering = ['-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        constraints = [
            models.UniqueConstraint(fields=['title'], name='unique_task_title')
        ]

    def __str__(self):
        return self.title


class SubTask(models.Model):
    STATUS_CHOICES = Task.STATUS_CHOICES  # We use the same statuses

    title = models.CharField(max_length=255, verbose_name="Task Title")
    description = models.TextField(blank=True, verbose_name="Task Description")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks', verbose_name="Main Task")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Task Status")
    deadline = models.DateTimeField(verbose_name="Deadline")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        db_table = 'task_manager_subtask'
        ordering = ['-created_at']
        verbose_name = 'SubTask'
        verbose_name_plural = 'SubTasks'
        constraints = [
            models.UniqueConstraint(fields=['title'], name='unique_subtask_title')
        ]

    def __str__(self):
        return f"{self.title} (Subtask of {self.task.title})"