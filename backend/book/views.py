from django.shortcuts import render

# Create your views here.
def book(request, book_id):
    return render(request, 'book/book.html', {'book': book_id})
