from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    published_date = models.DateField(null=True, blank=True)
    cover = models.ImageField(upload_to='books/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    categories = models.ManyToManyField('Category')
    stores = models.ManyToManyField('Store', through='BookStore')

    def __str__(self):
        return self.title


class Role(models.Model):
    title = models.CharField(max_length=50)

class BookAuthor(models.Model):
    role = models.OneToOneField(Role, on_delete=models.CASCADE)