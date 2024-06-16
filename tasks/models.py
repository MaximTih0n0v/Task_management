from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    phone_number = models.CharField(max_length=17, verbose_name='Номер телефона')
    is_customer = models.BooleanField(default=True, verbose_name='Заказчик')
    is_employee = models.BooleanField(default=False, verbose_name='Сотрудник')
    is_superadmin = models.BooleanField(default=False, verbose_name='СуперАдмин')
    patronymic = models.CharField(max_length=40, blank=True, null=True, verbose_name='Отчество')

    groups = models.ManyToManyField(Group, related_name='tasks_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='tasks_user_permissions_set', blank=True)

    class Meta:
        db_table = 'tasks_user'
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает исполнителя'),
        ('in_progress', 'В процессе'),
        ('completed', 'Выполнена')
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer = models.ForeignKey(User, related_name='created_tasks', on_delete=models.CASCADE)
    employee = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    report = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.report:
            raise ValueError("Отчет не может быть пустым при закрытии задачи")
        if self.status == 'completed' and not self.closed_at:
            self.closed_at = timezone.now()
        super().save(*args, **kwargs)

