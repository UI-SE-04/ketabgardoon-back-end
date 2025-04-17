from django.shortcuts import render

from authors.models import Author


# Create your views here.

def update_rating(request):
    user = request.GET.get('username')
    if user == 'all':
        for author in Author.objects.all():
            if author.total_number_of_ratings:
                author.update_rating()
    else:
        author = Author.objects.get(uername=user)
        author.update_rating()

def search_authors_by_name(request):
    string = request.GET.get('name')
    return Author.objects.filter(name__icontains=string)

def get_all_authors(request):
    authors = Author.objects.all()
    return {'authors': authors}
