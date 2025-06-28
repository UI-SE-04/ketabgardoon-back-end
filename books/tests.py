from django.db.models import Count, Avg
from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APIClient
from books.models import Book, Publisher, Author, Category, Store, BookStore, Rating, Role, BookAuthor
from books.serializers import BookSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from books.models import Book, Rating
from custom_users.models import CustomUser
from django.utils import timezone

class BookViewSetTests(TestCase):
    def setUp(self):
        # Initialize API client, user, book, and URLs for tests
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            description='Test Description'
        )
        self.url_list = '/api/v1/books/'
        self.url_detail = f'/api/v1/books/{self.book.id}/'

        # Clear cache before each test
        cache.clear()

    def test_list_books_default_sorting(self):
        # Test listing books with default sorting (Happy Path)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_books_sorted_by_views(self):
        # Test listing books sorted by view count (Happy Path)
        # Create another book with higher view count
        popular_book = Book.objects.create(
            title='Popular Book',
            view_count=100
        )

        response = self.client.get(self.url_list, {'sort': 'view'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], popular_book.id)

    def test_retrieve_book_authenticated_user(self):
        # Test retrieving book details for authenticated user (Happy Path)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book')

        # Verify view count incremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.view_count, 1)

    def test_retrieve_book_anonymous_user(self):
        # Test retrieving book details for anonymous user (Happy Path)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify view count incremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.view_count, 1)

    def test_view_count_once_per_day(self):
        # Test that view count increments only once per day per visitor (Edge Case)
        # First view
        response = self.client.get(self.url_detail)
        self.book.refresh_from_db()
        self.assertEqual(self.book.view_count, 1)

        # Second view on the same day
        response = self.client.get(self.url_detail)
        self.book.refresh_from_db()
        self.assertEqual(self.book.view_count, 1)  # Should not increment

    def test_retrieve_nonexistent_book(self):
        # Test retrieving a non-existent book (Error Case)
        response = self.client.get('/api/v1/books/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_books(self):
        # Test searching books by title (Happy Path)
        response = self.client.get(self.url_list, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Test search with no results
        response = self.client.get(self.url_list, {'search': 'Nonexistent'})
        self.assertEqual(len(response.data['results']), 0)

    def tearDown(self):
        # Clear cache after each test
        cache.clear()

class BookModelTests(TestCase):
    def setUp(self):
        # Initialize publisher, author, and category for tests
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.author = Author.objects.create(name='Test Author')
        self.category = Category.objects.create(title='Test Category')

    def test_create_book(self):
        # Test creating a book with relationships (Happy Path)
        book = Book.objects.create(
            title='Test Book',
            publisher=self.publisher
        )
        book.authors.add(self.author)
        book.categories.add(self.category)

        self.assertEqual(str(book), 'Test Book')
        self.assertEqual(book.authors.count(), 1)
        self.assertEqual(book.categories.count(), 1)

    def test_book_author_relationship(self):
        # Test book-author relationship (Edge Case)
        book = Book.objects.create(title='Test Book')
        author2 = Author.objects.create(name='Another Author')

        # Create book-author relationship
        BookAuthor.objects.create(
            book=book,
            author=self.author,
            role=None
        )

        self.assertEqual(book.bookauthor_set.count(), 1)

        # Add second author
        BookAuthor.objects.create(
            book=book,
            author=author2,
            role=None
        )

        self.assertEqual(book.authors.count(), 2)

    def test_book_string_representation(self):
        # Test book string representation with maximum length title (Edge Case)
        book = Book.objects.create(title='A' * 255)  # Max length
        self.assertEqual(str(book), 'A' * 255)

    def test_category_unique_title(self):
        # Test unique title constraint for category (Error Case)
        Category.objects.create(title='Unique Category')
        with self.assertRaises(Exception):
            Category.objects.create(title='Unique Category')

    def test_book_isbn_validation(self):
        # Test ISBN validation (Edge Case)
        book = Book.objects.create(title='ISBN Test')
        # Valid ISBN
        isbn = book.bookisbn_set.create(isbn='9783161484100')
        self.assertEqual(str(isbn), '9783161484100')

        # Invalid ISBN (duplicate)
        with self.assertRaises(Exception):
            book.bookisbn_set.create(isbn='9783161484100')

User = get_user_model()

class BookSerializerTests(TestCase):
    def setUp(self):
        # Initialize publisher, author, category, role, stores, book, and ratings for tests
        self.publisher = Publisher.objects.create(name='Test Publisher')
        self.author = Author.objects.create(name='Test Author')
        self.category = Category.objects.create(title='Test Category')
        self.role = Role.objects.create(title='Author')
        self.store1 = Store.objects.create(name='Store 1', website='https://store1.com')
        self.store2 = Store.objects.create(name='Store 2', website='https://store2.com')
        self.book = Book.objects.create(
            title='Test Book',
            publisher=self.publisher
        )
        BookAuthor.objects.create(
            book=self.book,
            author=self.author,
            role=self.role
        )
        self.book.categories.add(self.category)
        BookStore.objects.create(book=self.book, store=self.store1, url='https://store1.com/book1')
        BookStore.objects.create(book=self.book, store=self.store2, url='https://store2.com/book1')
        self.user = User.objects.create_user(username='testuser', password='password')
        Rating.objects.create(book=self.book, user=self.user, rating=4.5)
        self.client = APIClient()
        self.request = self.client.get('/').wsgi_request

    def test_book_serialization(self):
        # Test serializing book data (Happy Path)
        serializer = BookSerializer(
            instance=self.book,
            context={'request': self.request}
        )
        data = serializer.data

        self.assertEqual(data['title'], 'Test Book')
        self.assertEqual(len(data['authors']), 1)
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(len(data['stores']), 2)

    def test_store_data_in_serializer(self):
        # Test store data in serializer (Edge Case)
        serializer = BookSerializer(
            instance=self.book,
            context={'request': self.request}
        )
        store_data = serializer.data['stores'][0]

        self.assertIn('name', store_data)
        self.assertIn('logo', store_data)
        self.assertIn('url', store_data)
        self.assertTrue(store_data['url'].startswith('https://'))

        # Annotate book with rating fields
        book = Book.objects.annotate(
            ratings_count=Count('rating'),
            ratings_avg=Avg('rating__rating')
        ).get(pk=self.book.id)

        serializer = BookSerializer(book)
        data = serializer.data

        self.assertIn('ratings_count', data)
        self.assertIn('ratings_avg', data)
        self.assertEqual(data['ratings_count'], 1)
        self.assertEqual(data['ratings_avg'], 4.5)

    def test_serializer_with_invalid_data(self):
        # Test serializer with invalid data (Error Case)
        invalid_data = {
            'title': '',  # Required field
            'published_date': 'invalid-date'  # Wrong format
        }
        serializer = BookSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)
        self.assertIn('published_date', serializer.errors)

User = get_user_model()

class RatingsViewSetTests(APITestCase):
    def setUp(self):
        # Initialize users, books, and ratings for tests
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )
        self.book1 = Book.objects.create(title='Book One')
        self.book2 = Book.objects.create(title='Book Two')
        self.book3 = Book.objects.create(title='Book Three')
        self.rating1 = Rating.objects.create(
            user=self.user1,
            book=self.book1,
            rating=4.5
        )
        self.rating2 = Rating.objects.create(
            user=self.user1,
            book=self.book2,
            rating=3.0
        )
        Rating.objects.create(
            user=self.user2,
            book=self.book3,
            rating=5.0
        )

    def test_list_own_ratings_happy_path(self):
        # Test listing own ratings (Happy Path)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/books/ratings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['book'], self.book1.id)

    def test_retrieve_own_rating_happy_path(self):
        # Test retrieving own rating details (Happy Path)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/books/ratings/{self.rating1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4.5)

    def test_pagination_happy_path(self):
        # Test pagination of ratings list (Happy Path)
        self.client.force_authenticate(user=self.user1)

        # Create additional ratings for pagination testing
        for i in range(15):
            book = Book.objects.create(title=f'Book {i + 4}')
            Rating.objects.create(
                user=self.user1,
                book=book,
                rating=3.5
            )

        response = self.client.get('/api/v1/books/ratings/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)  # 17 total, 10 on page 1, 7 on page 2

    def test_access_unauthenticated_error(self):
        # Test accessing ratings without authentication (401 Error)
        response = self.client.get('/api/v1/books/ratings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_other_user_rating_error(self):
        # Test accessing another user's rating (404 Error)
        self.client.force_authenticate(user=self.user1)
        rating = Rating.objects.get(user=self.user2)
        response = self.client.get(f'/api/v1/books/ratings/{rating.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_no_ratings_happy_path(self):
        # Test user with no ratings (Edge Case)
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=new_user)
        response = self.client.get('/api/v1/books/ratings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_min_max_rating_values_happy_path(self):
        # Test ratings with minimum and maximum values (Edge Case)
        self.client.force_authenticate(user=self.user1)
        min_rating = Rating.objects.create(
            user=self.user1,
            book=self.book3,
            rating=0.5
        )
        max_rating = Rating.objects.create(
            user=self.user1,
            book=self.book3,
            rating=5.0
        )

        response = self.client.get(f'/api/v1/books/ratings/{min_rating.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 0.5)

        response = self.client.get(f'/api/v1/books/ratings/{max_rating.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5.0)

    def test_create_rating_via_ratings_endpoint_error(self):
        # Test creating rating via this view (405 Error)
        self.client.force_authenticate(user=self.user1)
        data = {'book': self.book3.id, 'rating': 4.0}
        response = self.client.post('/api/v1/books/ratings/', data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_rating_via_ratings_endpoint_error(self):
        # Test updating rating via this view (405 Error)
        self.client.force_authenticate(user=self.user1)
        data = {'rating': 4.5}
        response = self.client.patch(f'/api/v1/books/ratings/{self.rating1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_rating_via_ratings_endpoint_error(self):
        # Test deleting rating via this view (405 Error)
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/v1/books/ratings/{self.rating1.id}/')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_sort_ratings_by_book_title_happy_path(self):
        # Test sorting ratings by book title (Happy Path)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/books/ratings/?ordering=book__title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['book'], self.book1.id)  # Book One
        self.assertEqual(response.data['results'][1]['book'], self.book2.id)  # Book Two

    def test_sort_ratings_by_rating_value_happy_path(self):
        """مرتب‌سازی امتیازها بر اساس مقدار امتیاز (حالت عادی)"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/books/ratings/?ordering=-rating')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['rating'], 4.5)
        self.assertEqual(response.data['results'][1]['rating'], 3.0)