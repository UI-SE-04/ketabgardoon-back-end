from django.db import models

from countries.models import Nationality

# Create your models here.
class Author(models.Model):
    def update_rating(self):
        self.rating = self.total_sum_of_ratings / self.total_number_of_ratings
        self.save()

    name = models.CharField(max_length=255)
    birth_date = models.DateField(blank=True, null=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.FloatField(blank=True, null=True)
    total_sum_of_ratings = models.IntegerField(blank=True, null=True)
    total_number_of_ratings = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    author_photo = models.ImageField(upload_to='author_photos/', blank=True, null=True)
    call_info = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
