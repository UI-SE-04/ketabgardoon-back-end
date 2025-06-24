from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, pagination
from django.db.models import Q
import re
from books.models import Book, Author, Category,BookISBN
from custom_users.models import CustomUser
from .serializers import BookSerializer, AuthorSerializer, UserSerializer,CategorySerializer

class SearchPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SearchView(APIView):
    pagination_class = SearchPagination

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ISBN regex pattern for 10 or 13 digits (with optional hyphens)
        isbn_pattern = r'^(?=(?:[^0-9]*[0-9]){10}(?:(?:[^0-9]*[0-9]){3})?$)[\\d-]+$'
        results = {
            'books': [],
            'authors': [],
            'users': [],
        }

        if re.match(isbn_pattern, query):
            # Search by ISBN
            isbn_results = BookISBN.objects.filter(isbn=query.replace('-', '')).select_related('book')
            books = [isbn.book for isbn in isbn_results]
            book_serializer = BookSerializer(books, many=True)
            results['books'] = book_serializer.data
        else:
            # Search books by title
            book_results = Book.objects.filter(
                Q(title__icontains=query)
            ).distinct().prefetch_related('authors', 'categories')
            book_serializer = BookSerializer(book_results, many=True)
            results['books'] = book_serializer.data

            # Search authors by name
            author_results = Author.objects.filter(
                Q(name__icontains=query)
            ).distinct().select_related('nationality')
            author_serializer = AuthorSerializer(author_results, many=True)
            results['authors'] = author_serializer.data

            # Search users by username, first name, or last name
            user_results = CustomUser.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).distinct()
            user_serializer = UserSerializer(user_results, many=True)
            results['users'] = user_serializer.data

            # Search categories and add their books to the books list
            category_results = Category.objects.filter(
                Q(title__icontains=query)
            ).distinct()
            if category_results.exists():
                category_books = Book.objects.filter(
                    categories__in=category_results
                ).distinct().prefetch_related('authors', 'categories')
                category_book_serializer = BookSerializer(category_books, many=True)
                # avoiding duplicates
                existing_book_ids = {book['id'] for book in results['books']}
                results['books'].extend(
                    [book for book in category_book_serializer.data if book['id'] not in existing_book_ids]
                )

        # Apply pagination
        paginator = self.pagination_class()
        paginated_results = paginator.paginate_queryset([results], request)
        return paginator.get_paginated_response(paginated_results[0])


class CategorySearchView(APIView):
    pagination_class = SearchPagination

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        category_results = Category.objects.filter(
            Q(title__icontains=query)
        ).distinct().prefetch_related('book_set__authors')

        paginator = self.pagination_class()
        paginated_categories = paginator.paginate_queryset(category_results, request)

        serializer = CategorySerializer(paginated_categories, many=True)
        return paginator.get_paginated_response(serializer.data)