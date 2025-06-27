from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, pagination
from django.db.models import Q,Prefetch
import re
from books.models import Book, Author, Category,BookISBN
from custom_users.models import CustomUser
from .serializers import BookSerializer, AuthorSerializer, UserSerializer,CategorySerializer
from pyuca import Collator

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
        collator = Collator()  # Persian alphabet sorting
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
            # Apply Persian sorting for title using pyuca
            if sort_field == 'title':
                books = sorted(books, key=lambda x: collator.sort_key(x.title or ''))
            elif sort_field == '-title':
                books = sorted(books, key=lambda x: collator.sort_key(x.title or ''), reverse=True)
            elif sort_field in valid_book_sorts:
                books = sorted(books, key=lambda x: (
                    getattr(x, sort_field.lstrip('-')) or 0
                    if not sort_field.startswith('-') else -(getattr(x, sort_field.lstrip('-')) or 0)
                ))
            book_serializer = BookSerializer(books, many=True)
            results['books'] = book_serializer.data
        else:
            # Search books by title
            book_results = Book.objects.filter(
                Q(title__icontains=query)
            ).distinct().prefetch_related('authors', 'categories')
            # CHANGE: Use Python sorting with pyuca for title to support Persian alphabet
            if sort_field == 'title' or sort_field == '-title':
                book_results = sorted(
                    book_results,
                    key=lambda x: collator.sort_key(x.title or ''),
                    reverse=(sort_field == '-title')
                )
                book_serializer = BookSerializer(book_results, many=True)
                results['books'] = book_serializer.data
            else:
                if sort_field in valid_book_sorts:
                    book_results = book_results.order_by(sort_field)
                book_serializer = BookSerializer(book_results, many=True)
                results['books'] = book_serializer.data

            # Search categories and add their books to books list
            category_results = Category.objects.filter(
                Q(title__icontains=query)
            ).distinct()
            if category_results.exists():
                category_books = Book.objects.filter(
                    categories__in=category_results
                ).distinct().prefetch_related('authors', 'categories')
                # sorting for category books (Persian for title)
                if sort_field == 'title' or sort_field == '-title':
                    category_books = sorted(
                        category_books,
                        key=lambda x: collator.sort_key(x.title or ''),
                        reverse=(sort_field == '-title')
                    )
                    category_book_serializer = BookSerializer(category_books, many=True)
                else:
                    if sort_field in valid_book_sorts:
                        category_books = category_books.order_by(sort_field)
                    category_book_serializer = BookSerializer(category_books, many=True)
                # Merge books, avoiding duplicates
                existing_book_ids = {book['id'] for book in results['books']}
                results['books'].extend(
                    [book for book in category_book_serializer.data if book['id'] not in existing_book_ids]
                )

            # Search authors by name
            author_results = Author.objects.filter(
                Q(name__icontains=query)
            ).distinct().select_related('nationality')
            # sorting with pyuca for name for Persian alphabet
            if sort_field == 'name' or sort_field == '-name':
                author_results = sorted(
                    author_results,
                    key=lambda x: collator.sort_key(x.name or ''),
                    reverse=(sort_field == '-name')
                )
                author_serializer = AuthorSerializer(author_results, many=True)
                results['authors'] = author_serializer.data
            else:
                author_serializer = AuthorSerializer(author_results, many=True)
                results['authors'] = author_serializer.data

            # Search users by username, first name, or last name
            user_results = CustomUser.objects.filter(
                Q(username__icontains=query)
            ).distinct()
            # sorting with pyuca for username for Persian alphabet
            if sort_field == 'username' or sort_field == '-username':
                user_results = sorted(
                    user_results,
                    key=lambda x: collator.sort_key(x.username or ''),
                    reverse=(sort_field == '-username')
                )
                user_serializer = UserSerializer(user_results, many=True)
                results['users'] = user_serializer.data
            else:
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
        sort = request.query_params.get('sort', '').strip()
        if not query:
            return Response(
                {'error': 'Query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # valid sort options for books
        valid_book_sorts = ['title', '-title', 'published_date', '-published_date', 'page_count', '-page_count']
        sort_field = sort if sort in valid_book_sorts else None
        collator = Collator()

        # Initial category query
        category_results = Category.objects.filter(
            Q(title__icontains=query)
        ).distinct()

        # Sorting for books within categories
        if sort_field in valid_book_sorts:
            if sort_field in ['title', '-title']:
                # Use a list to store sorted books for each category
                sorted_categories = []
                for category in category_results:
                    # Fetch books for the category
                    books = list(category.book_set.all().prefetch_related('authors'))
                    # Sort books in Python using pyuca for Persian titles
                    sorted_books = sorted(
                        books,
                        key=lambda x: collator.sort_key(x.title or ''),
                        reverse=(sort_field == '-title')
                    )
                    # Only include categories with books
                    if sorted_books:
                        # Create a new QuerySet for books to use in Prefetch
                        book_ids = [book.id for book in sorted_books]
                        sorted_books_queryset = Book.objects.filter(id__in=book_ids).prefetch_related('authors')
                        # Attach sorted books to category using Prefetch
                        category = Category.objects.filter(id=category.id).prefetch_related(
                            Prefetch('book_set', queryset=sorted_books_queryset)
                        ).first()
                        sorted_categories.append(category)
                category_results = sorted_categories
            else:
                # Use database sorting for other fields
                category_results = category_results.prefetch_related(
                    Prefetch('book_set', queryset=Book.objects.order_by(sort_field).prefetch_related('authors'))
                )
        else:
            # Default prefetch without sorting
            category_results = category_results.prefetch_related('book_set__authors')

        # Filter out categories with no books
        category_results = [cat for cat in category_results if cat.book_set.exists()]
        # Apply pagination
        paginator = self.pagination_class()
        paginated_categories = paginator.paginate_queryset(category_results, request)
        serializer = CategorySerializer(paginated_categories, many=True)
        return paginator.get_paginated_response(serializer.data)