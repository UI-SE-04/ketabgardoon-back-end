from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_private = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        default='default_pics/default_profile_pic.jpg'
    )
    bio = models.TextField(blank=True, null=True)
    # for authentication
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_temporary = models.BooleanField(default=False)
    verification_code_expiry = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.username
