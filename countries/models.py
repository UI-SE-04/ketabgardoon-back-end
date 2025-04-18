from django.db import models

# Create your models here.

class Nationality(models.Model):
    country = models.CharField(max_length=255)
    country_code = models.CharField(max_length=2)

    def __str__(self):
        return self.country