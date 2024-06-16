from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Task, User

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'patronymic', 'email', 'phone_number', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            last_name=validated_data['last_name'],
            first_name=validated_data['first_name'],
            patronymic=validated_data['patronymic'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password']
        )
        user.is_customer = True
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'first_name', 'patronymic', 'email', 'phone_number', 'is_customer',
                  'is_employee', 'is_superadmin']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'customer', 'employee', 'created_at', 'updated_at',
                  'closed_at', 'report']
        read_only_fields = ['customer', 'created_at', 'updated_at', 'closed_at']
