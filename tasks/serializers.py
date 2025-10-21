from rest_framework import serializers
from .models import Task, TaskList
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskListSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = TaskList
        fields = ['id', 'name', 'created_by']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        return TaskList.objects.create(created_by=user, **validated_data)


class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.CharField(source='assignee.username', read_only=True)
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    list = serializers.CharField(source='list.name', read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    list_id = serializers.PrimaryKeyRelatedField(
        queryset=TaskList.objects.all(),
        source='list',
        write_only=True
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'due_date',
            'is_done',
            'assignee',
            'created_by',
            'list',
            'assignee_id',
            'list_id',
        ]
    
    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        return Task.objects.create(created_by=user, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance