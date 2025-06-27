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
        sort = request.query_params.get('sort', '').strip()
        if not query:
            return Response(
                {'error': 'Query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # valid sort options for books, authors, and users
        valid_book_sorts = ['title', '-title', 'published_date', '-published_date', 'page_count', '-page_count']
        valid_author_user_sorts = ['name', '-name', 'username', '-username']
        sort_field = sort if sort in valid_book_sorts + valid_author_user_sorts else None

        # ISBN regex pattern for 10 or 13 digits (with optional hyphens)
        isbn_pattern = r'^(?:\d{10}|\d{13}|[\d-]{10,17})$'
        results = {
            'books': [],
            'authors': [],
            'users': [],
        }

        if re.match(isbn_pattern, query):
            # Search by ISBN (support both with and without hyphens)
            cleaned_isbn = query.replace('-', '')
            isbn_results = BookISBN.objects.filter(
                isbn__in=[query, cleaned_isbn]
            ).select_related('book')
            books = [isbn.book for isbn in isbn_results]
            # Apply sorting for ISBN search results
            if sort_field in valid_book_sorts:
                books = sorted(books, key=lambda x: (
                    getattr(x, sort_field.lstrip('-')) or ''
                    if not sort_field.startswith('-') else -(getattr(x, sort_field.lstrip('-')) or 0)
                ))
            book_serializer = BookSerializer(books, many=True)
            results['books'] = book_serializer.data
        else:
            # Search books by title
            book_results = Book.objects.filter(
                Q(title__icontains=query)
            ).distinct().prefetch_related('authors', 'categories')
            if sort_field in valid_book_sorts:
                book_results = book_results.order_by(sort_field)
            # Search categories and add their books
            category_results = Category.objects.filter(
                Q(title__icontains=query)
            ).distinct()
            if category_results.exists():
                category_books = Book.objects.filter(
                    categories__in=category_results
                ).distinct().prefetch_related('authors', 'categories')
            # sorting for category books
                if sort_field in valid_book_sorts:
                  category_books = category_books.order_by(sort_field)
                category_book_serializer = BookSerializer(category_books, many=True)
                book_serializer = BookSerializer(book_results, many=True)
            # Merge books, avoiding duplicates
                existing_book_ids = {book['id'] for book in book_serializer.data}
                results['books'] = book_serializer.data + [
                  book for book in category_book_serializer.data if book['id'] not in existing_book_ids]
            else:
                book_serializer = BookSerializer(book_results, many=True)
                results['books'] = book_serializer.data

            # Search authors by name
            author_results = Author.objects.filter(
                Q(name__icontains=query)
            ).distinct().select_related('nationality')
            # sorting for authors
            if sort_field == 'name' or sort_field == '-name':
                author_results = author_results.order_by(sort_field)
            author_serializer = AuthorSerializer(author_results, many=True)
            results['authors'] = author_serializer.data

            # Search users by username, first name, or last name
            user_results = CustomUser.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).distinct()
            # sorting for users
            if sort_field == 'username' or sort_field == '-username':
                user_results = user_results.order_by(sort_field)
            user_serializer = UserSerializer(user_results, many=True)
            results['users'] = user_serializer.data
        # Apply pagination
        paginator = self.pagination_class()
        paginated_results = paginator.paginate_queryset([results], request)
        return paginator.get_paginated_response(paginated_results[0])


class CategorySearchView(APIView):
    pagination_class = SearchPagination

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        # sort parameter from query params
        sort = request.query_params.get('sort', '').strip()
        if not query:
            return Response(
                {'error': 'Query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # valid sort options for books
        valid_book_sorts = ['title', '-title', 'published_date', '-published_date', 'page_count', '-page_count']
        sort_field = sort if sort in valid_book_sorts else None

        category_results = Category.objects.filter(
            Q(title__icontains=query)
        ).distinct().prefetch_related('book_set__authors')


        paginator = self.pagination_class()
        paginated_categories = paginator.paginate_queryset(category_results, request)

        serializer = CategorySerializer(paginated_categories, many=True)
        return paginator.get_paginated_response(serializer.data)