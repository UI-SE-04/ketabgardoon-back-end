from django.shortcuts import render

# Create your views here.
def book(request, book_id):
    return render(request, 'books/books.html', {'books': book_id})
