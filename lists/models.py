from django.db import models
from django.db.models import ForeignKey

from books.models import Book
from custom_users.models import CustomUser

class ListIcon(models.Model):
    icon = models.ImageField(
        upload_to="lists/icons/",
        help_text="SVG or PNG icon representing the list."
    )

    def __str__(self):
        return f"Icon {self.pk}"


class List(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="lists")
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    icon_id = ForeignKey(ListIcon, on_delete=models.PROTECT, related_name="lists_using")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class BookList(models.Model):
    class Meta:
        unique_together = ('book', 'list')

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="in_lists" )
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name="book_entries")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.list.name} - {self.list.user.username} - {self.book.title}"





