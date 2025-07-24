from django.contrib import admin
from .models import Task, SubTask, Category


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class SubtaskInline(admin.TabularInline):
    model = SubTask
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'status', 'deadline', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at', 'categories')
    search_fields = ('title', 'description')
    filter_horizontal = ('categories',)
    inlines = [SubtaskInline]

    def short_title(self, obj):
        return (obj.title[:10] + '...') if len(obj.title) > 10 else obj.title

    short_title.short_description = 'Title'

    def update_status(self, request, queryset):
        queryset.update(status='done')
    actions = [update_status]


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')