from django.db import models
from authors.models import Author
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
    title = models.CharField(max_length=255)

class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

class BookISBN(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=13, unique=True)