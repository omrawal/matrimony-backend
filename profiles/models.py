from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    age = models.IntegerField(null=True, blank=True)
    cast = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    preferences = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        # Fallback string formatting to avoid NoneType concatenation errors
        f_name = self.first_name or ""
        l_name = self.last_name or ""
        name_str = f" ({f_name} {l_name})".strip()
        return f"{self.username}{name_str if f_name or l_name else ''}"


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


class UserPhoto(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='photos')
    image_url = models.URLField(max_length=500)
    public_id = models.CharField(max_length=255) # Required to delete images from Cloudinary later
    is_profile_pic = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_profile_pic', '-uploaded_at'] # Profile pic always appears first

    def __str__(self):
        return f"{self.user.username} - Photo"

class IDProof(models.Model):
    user = models.ForeignKey(CustomUser, related_name='id_proofs', on_delete=models.CASCADE)
    image_url = models.URLField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"ID Proof for {self.user.email}"