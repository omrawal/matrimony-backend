from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    age = models.IntegerField(null=True, blank=True)
    cast = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    preferences = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username


class ProfileViewLog(models.Model):
    visitor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='views_performed'
    )
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='views_received'
    )
    # Changed from auto_now_add=True to explicit default for updates
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        # Enforces uniqueness at the database level
        constraints = [
            models.UniqueConstraint(fields=['visitor', 'host'], name='unique_visitor_host_pair')
        ]

    def __str__(self):
        return f"{self.visitor.username} viewed {self.host.username} last at {self.timestamp}"
    