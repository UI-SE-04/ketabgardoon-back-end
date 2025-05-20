from django.db import models

from books.models import Book
from custom_users.models import CustomUser

class List(models.Model):
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    icon_id = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class BookList(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

