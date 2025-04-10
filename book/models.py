from django.db import models

class Publisher(models.Model):
    pass


class Author(models.Model):
    pass

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    publisher = models.ForeignKey(Publisher, null=True, blank=True, on_delete=models.SET_NULL, related_name='books')
    published_date = models.DateField(null=True, blank=True)
    cover = models.ImageField(null=True, blank=True)  # Consider ImageField for file-based images.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationship with authors is managed via a through model.
    authors = models.ManyToManyField(Author, through='BookAuthor', related_name='books')

    def __str__(self):
        return self.title


