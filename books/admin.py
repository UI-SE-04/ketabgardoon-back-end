from django.contrib import admin
from books.models import Book, Publisher, BookAuthor, Role, BookISBN, Category, Store, BookStore, Rating

# Register your models here.
admin.site.register(Book)
admin.site.register(Publisher)
admin.site.register(BookAuthor)
admin.site.register(Role)
admin.site.register(BookISBN)
admin.site.register(Category)
admin.site.register(Store)
admin.site.register(BookStore)
admin.site.register(Rating)

