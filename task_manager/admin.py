from django.contrib import admin
from .models import Task, SubTask, Category


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'deadline', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at', 'categories')
    search_fields = ('title', 'description')
    filter_horizontal = ('categories',)


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')