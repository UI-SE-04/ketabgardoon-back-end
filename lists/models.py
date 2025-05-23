from django.db import models

from books.models import Book
from custom_users.models import CustomUser


class List(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="lists")
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    icon_filename = models.CharField(max_length=100, help_text="Filename from /media/lists/icons/", default='default.png')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def get_icon_url(self):
        from django.conf import settings
        return f"{settings.MEDIA_URL}lists/icons/{self.icon_filename}"


class BookList(models.Model):
    class Meta:
        unique_together = ('book', 'list')

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="in_lists" )
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="book_entries")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.list.name} - {self.list.user.username} - {self.book.title}"





