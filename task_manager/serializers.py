from datetime import date
from rest_framework import serializers
from .models import Task, SubTask, Category
from django.contrib.auth.models import User
import re


class TaskModelSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Task
        fields = ['owner', 'title', 'description', 'status', 'deadline', 'categories']
        read_only_fields = ['owner']

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        task = Task.objects.create(**validated_data)  # owner задаётся в view
        if categories:
            task.categories.set(categories)
        return task


class SubTaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


    class Meta:
        model = SubTask
        fields = ['owner','title', 'description', 'task', 'status', 'deadline', 'created_at']
        read_only_fields = ['owner', 'created_at']


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
    owner = serializers.StringRelatedField(read_only=True)


    class Meta:
        model = Task
        fields = ['owner','title', 'description', 'status', 'deadline', 'subtasks']
        read_only_fields = ['owner']

class TaskCreateSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)


    class Meta:
        model = Task
        fields = ['owner','title', 'description', 'status', 'deadline']
        read_only_fields = ['owner']

    def validate_deadline(self, value):
        if value < date.today():
            raise serializers.ValidationError({'deadline': f'Deadline must be greater than {date.today()}'})
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        def validate_email(self, value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError({'email': f'User with email {value} already exists'})
            return value

        def validate_password(self, data):
            if data['password1'] != data['password2']:
                raise serializers.ValidationError({'password': f'Passwords must match'})
            if not re.search(r"[A-Za-z]", data['password1']) or not re.search(r"\d", data['password1']):
                raise serializers.ValidationError({"password": f'Passwords must contain at least one number'})
            return data

        def create(self, validated_data):
            validated_data.pop('password2')
            user = User(
                username=validated_data['username'],
                email=validated_data['email'])
            user.set_password(validated_data['password1'])
            user.save()
            return user