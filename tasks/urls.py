from django.urls import path
from .views import (TokenObtainPairView, UserDetailView, TaskListCreateView, TaskDetailView, UserListCreateView,
                    UserRegistrationView, assign_task_to_self, close_task, TaskUpdateView)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/me/', UserDetailView.as_view(), name='user_detail'),
    path('api/tasks/', TaskListCreateView.as_view(), name='task_list_create'),
    path('api/tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('api/users/', UserListCreateView.as_view(), name='user_list_create'),
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/task/<int:task_id>/assign/', assign_task_to_self, name='assign_task_to_self'),
    path('api/task/<int:task_id>/close/', close_task, name='close_task'),
    path('api/task/<int:pk>/edit/', TaskUpdateView.as_view(), name='task_edit'),
]
