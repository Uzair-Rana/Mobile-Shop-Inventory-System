from django.contrib.auth.models import AbstractUser
from django.db import models


class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    role_display = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_superuser = models.BooleanField(default=False)
    branches = models.JSONField(default=list)   # list of branch IDs

    @property
    def permissions_list(self):
        if self.is_superuser:
            return list(Permission.objects.values_list('codename', flat=True))
        if self.role:
            return list(self.role.permissions.values_list('codename', flat=True))
        return []

    def __str__(self):
        return self.username
