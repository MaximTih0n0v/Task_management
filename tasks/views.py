from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Task, User
from .serializers import TaskSerializer, UserSerializer, UserRegistrationSerializer
from .permissions import IsOwnerOrReadOnly, IsSuperAdmin, IsEmployeeOrSuperAdmin


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer


class TokenObtainPairView(TokenObtainPairView):
    pass


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_superadmin:
            return Task.objects.all()
        if user.is_employee:
            return Task.objects.filter(employee=user) | Task.objects.filter(employee__isnull=True)
        return Task.objects.filter(customer=user)


class TaskDetailView(generics.RetrieveUpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        task = super().get_object()
        user = self.request.user
        if task.customer == user or task.employee == user or user.is_superadmin:
            return task
        else:
            raise PermissionDenied("У вас нет доступа к этой задаче")


class TaskUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'completed':
            return Response({'error': 'Нельзя редактировать закрытую задачу.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(customer=user)


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsEmployeeOrSuperAdmin()]

    def perform_create(self, serializer):
        serializer.save(is_customer=True)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_task_to_self(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена!'}, status=status.HTTP_404_NOT_FOUND)

    if task.employee is not None:
        return Response({'error': 'Задача уже назначена другому сотруднику...'}, status=status.HTTP_400_BAD_REQUEST)

    task.employee = request.user
    task.status = 'in_progress'
    task.save()

    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена!'}, status=status.HTTP_404_NOT_FOUND)

    if task.status == 'completed':
        return Response({'error': 'Закрытую задачу запрещено редактировать!'}, status=status.HTTP_403_FORBIDDEN)

    if task.employee != request.user and not request.user.is_superadmin:
        return Response({'error': 'У вас нет доступа для закрытия этой задачи!'}, status=status.HTTP_403_FORBIDDEN)

    report = request.data.get('report', '').strip()
    if not report:
        return Response({'error': 'Поле "report" не может быть пустым при закрытии задачи!'},
                        status=status.HTTP_400_BAD_REQUEST)

    task.status = 'completed'
    task.report = report
    task.save()

    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)
