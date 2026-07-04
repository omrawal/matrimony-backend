from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import RegexValidator
from datetime import date

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Phone number must be exactly 10 digits.")
    phone_number = models.CharField(validators=[phone_regex], max_length=10, unique=True, null=True, blank=True)

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    # --- REPLACED: age is now calculated from date_of_birth ---
    date_of_birth = models.DateField(null=True, blank=True) 
    
    cast = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    preferences = models.TextField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    # --- NEW SENSITIVE DETAILS ---
    time_of_birth = models.TimeField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=255, null=True, blank=True)
    astrology = models.CharField(max_length=50, null=True, blank=True) # e.g., Manglik, Shani
    diet = models.CharField(max_length=50, null=True, blank=True) # e.g., Veg, Non-Veg
    drink = models.CharField(max_length=50, null=True, blank=True) # e.g., Never, Occasionally
    mother_name = models.CharField(max_length=150, null=True, blank=True)
    father_name = models.CharField(max_length=150, null=True, blank=True)
    mother_contact = models.CharField(max_length=15, null=True, blank=True)
    father_contact = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    @property
    def age(self):
        """Dynamically calculates age based on DOB"""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    def save(self, *args, **kwargs):
        is_new_user = self.pk is None
        
        if is_new_user and self.is_superuser:
            super().save(*args, **kwargs)
            return
        
        if is_new_user and not self.username:
            self.username = "TEMP_USER"
            
        super().save(*args, **kwargs) 
        
        if is_new_user and not self.is_superuser:
            self.username = f"BSS{self.pk:04d}"
            super().save(update_fields=['username'])

    def __str__(self):
        f_name = self.first_name or ""
        l_name = self.last_name or ""
        name_str = f" ({f_name} {l_name})".strip()
        return f"{self.username}{name_str if f_name or l_name else ''}"

# --- NEW: TRACKING MODEL FOR LIMITS ---
class ContactViewLog(models.Model):
    viewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts_viewed')
    viewed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contact_viewers')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

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