from django.contrib import admin
from books.models import Book , Publisher,BookAuthor,Role,BookISBN,Category,Store,BookStore
# Register your models here.


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'publisher', 'published_date', 'view_count']
    list_filter = ['publisher', 'categories', 'published_date']
    filter_horizontal = ['categories']
    search_fields = ['title', 'description']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


admin.site.register(Publisher)
admin.site.register(Store)
admin.site.register(Role)
admin.site.register(BookAuthor)
admin.site.register(BookISBN)
admin.site.register(BookStore)