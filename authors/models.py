from django.db import models

from countries.models import Country

class Author(models.Model):
    name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    nationality = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    author_photo = models.ImageField(upload_to='author_photos/', blank=True, null=True)
    call_info = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
