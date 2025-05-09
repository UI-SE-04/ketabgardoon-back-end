from django.db import models
from authors.models import Author

class Publisher(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='publishers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    publisher = models.ForeignKey(Publisher, null=True, blank=True, on_delete=models.SET_NULL)
    published_date = models.DateField(null=True, blank=True)
    cover = models.ImageField(upload_to='books/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    authors = models.ManyToManyField(Author, through='BookAuthor')
    categories = models.ManyToManyField('Category')
    stores = models.ManyToManyField('Store', through='BookStore')

    def __str__(self):
        return self.title


class Role(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added_at']  # Orders by 'added_at' ascending by default

    def __str__(self):
        return f"{self.author.name} - {self.book.title}"


class BookISBN(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=13, unique=True)

    def __str__(self):
        return self.isbn

class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

class Store(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    logo = models.ImageField(upload_to='stores/', blank=True, null=True)

    def __str__(self):
        return self.name

class BookStore(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    url = models.URLField()

    def __str__(self):
        return f"{self.store.name} - {self.book.title}"