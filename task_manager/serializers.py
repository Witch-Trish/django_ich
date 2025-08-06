from datetime import date
from rest_framework import serializers
from .models import Task, SubTask, Category


class TaskModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields =['title','description', 'status', 'deadline']


class SubTaskCreateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = SubTask
        fields = ['title', 'description', 'task', 'status', 'deadline', 'created_at']


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'

    def create(self, validated_data):
        name = validated_data.get('name')

        if Category.objects.filter(name=name).exists():
            raise serializers.ValidationError({'name': f'Category with name {name} already exists'})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        name = validated_data.get('name', instance.name)
        if name != instance.name and Category.objects.filter(name=name).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({'name': f'Category with name {name} already exists'})
        return super().update(instance, validated_data)


class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskCreateSerializer(many=True, read_only=True)


    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'deadline', 'subtasks']


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'deadline']

        def validate_deadline(self, value):
            if value < date.today():
                raise serializers.ValidationError({'deadline': f'Deadline must be greater than {date.today()}'})
            return value