from django.test import TestCase, RequestFactory
from rest_framework.test import APIClient
from rest_framework import status
import json
from django.contrib.auth import get_user_model
from django_filters import FilterSet
from custom_users.models import CustomUser
from custom_users.serializers import CustomUserSerializer
from lists.models import List, BookList
from lists.filters import ListFilter
from lists.serializers import ListSerializer, BookListCreateSerializer
from books.models import Book

User = get_user_model()

class ListModelTests(TestCase):
    def setUp(self):
        # Initialize user for list model tests
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

    def test_create_list_success(self):
        # Test successful list creation (Happy Path)
        lst = List.objects.create(
            name='Test List',
            user=self.user,
            is_public=True
        )
        self.assertEqual(str(lst), 'Test List - testuser')
        self.assertEqual(lst.get_icon_url(), '/media/lists/icons/default.png')

    def test_unique_list_name_per_user(self):
        # Test unique list name constraint per user (Error Case)
        List.objects.create(name='My List', user=self.user)
        with self.assertRaises(Exception):
            List.objects.create(name='My List', user=self.user)

    def test_multiple_users_same_list_name(self):
        # Test multiple users can have same list name (Edge Case)
        user2 = User.objects.create_user(username='user2')
        List.objects.create(name='Shared List', user=self.user)
        List.objects.create(name='Shared List', user=user2)
        self.assertEqual(List.objects.filter(name='Shared List').count(), 2)

    def test_list_icon_url(self):
        # Test custom icon URL (Edge Case)
        lst = List.objects.create(
            name='Custom Icon',
            user=self.user,
            icon='custom.png'
        )
        self.assertEqual(lst.get_icon_url(), '/media/lists/icons/custom.png')

class BookListModelTests(TestCase):
    def setUp(self):
        # Initialize user, list, and book for book list model tests
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.lst = List.objects.create(name='Test List', user=self.user)
        self.book = Book.objects.create(title='Test Book')

    def test_create_book_list_entry(self):
        # Test successful BookList creation (Happy Path)
        entry = BookList.objects.create(
            list=self.lst,
            book=self.book
        )
        self.assertEqual(str(entry), 'Test List - testuser - Test Book')

    def test_unique_book_per_list(self):
        # Test unique book per list constraint (Error Case)
        BookList.objects.create(list=self.lst, book=self.book)
        with self.assertRaises(Exception):
            BookList.objects.create(list=self.lst, book=self.book)

    def test_same_book_different_lists(self):
        # Test same book can be in different lists (Edge Case)
        lst2 = List.objects.create(name='Another List', user=self.user)
        BookList.objects.create(list=self.lst, book=self.book)
        BookList.objects.create(list=lst2, book=self.book)
        self.assertEqual(BookList.objects.count(), 2)

class ListSerializerTests(TestCase):
    def setUp(self):
        # Initialize user, list, and client for list serializer tests
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.list = List.objects.create(
            name='Test List',
            user=self.user,
            is_public=True
        )
        self.client = APIClient()
        self.request = self.client.get('/').wsgi_request

    def test_list_serialization(self):
        # Test serializing list data (Happy Path)
        serializer = ListSerializer(
            instance=self.list,
            context={'request': self.request}
        )
        data = serializer.data
        self.assertEqual(data['name'], 'Test List')
        self.assertTrue(data['is_public'])
        self.assertEqual(data['icon'], '/media/lists/icons/default.png')

    def test_create_list_missing_name(self):
        # Test creating list without name (Error Case)
        data = {'is_public': True}
        serializer = ListSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

class BookListCreateSerializerTests(TestCase):
    def setUp(self):
        # Initialize user, list, and book for book list serializer tests
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.list = List.objects.create(name='Test List', user=self.user)
        self.book = Book.objects.create(title='Test Book')

    def test_add_book_to_list(self):
        # Test adding book to list (Happy Path)
        data = {'book_id': self.book.id}
        serializer = BookListCreateSerializer(
            data=data,
            context={'list_obj': self.list}
        )
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.assertEqual(instance.list, self.list)
        self.assertEqual(instance.book, self.book)

    def test_add_nonexistent_book(self):
        # Test adding non-existent book to list (Error Case)
        data = {'book_id': 999}
        serializer = BookListCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('book_id', serializer.errors)

    def test_duplicate_book_in_list(self):
        # Test adding duplicate book to list (Error Case)
        BookList.objects.create(list=self.list, book=self.book)
        data = {'book_id': self.book.id}
        serializer = BookListCreateSerializer(
            data=data,
            context={'list_obj': self.list}
        )
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(Exception):
            serializer.save()

class ListViewSetTests(TestCase):
    def setUp(self):
        # Initialize client, users, lists, and books for viewset tests
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123'
        )
        self.private_list = List.objects.create(
            name='Private List',
            user=self.user,
            is_public=False
        )
        self.public_list = List.objects.create(
            name='Public List',
            user=self.user,
            is_public=True
        )
        self.other_user_list = List.objects.create(
            name='Other User List',
            user=self.other_user,
            is_public=False
        )
        self.book1 = Book.objects.create(title='Book 1')
        self.book2 = Book.objects.create(title='Book 2')
        self.client.force_authenticate(user=self.user)

    def test_list_own_lists(self):
        # Test listing user's own lists (Happy Path)
        response = self.client.get('/api/v1/lists/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_public_lists_anonymous(self):
        # Test listing public lists as anonymous user (Happy Path)
        self.client.logout()
        response = self.client.get('/api/v1/lists/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Public List')

    def test_create_list_success(self):
        # Test creating list successfully (Happy Path)
        data = {'name': 'New List', 'is_public': True}
        response = self.client.post('/api/v1/lists/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(List.objects.count(), 4)

    def test_update_own_list(self):
        # Test updating own list (Happy Path)
        data = {'name': 'Updated List', 'is_public': False}
        response = self.client.put(
            f'/api/v1/lists/{self.private_list.id}/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.private_list.refresh_from_db()
        self.assertEqual(self.private_list.name, 'Updated List')

    def test_update_other_user_list(self):
        # Test updating other user's list (Security Case)
        data = {'name': 'Hacked List'}
        response = self.client.put(
            f'/api/v1/lists/{self.other_user_list.id}/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_list_success(self):
        # Test deleting list successfully (Happy Path)
        response = self.client.delete(f'/api/v1/lists/{self.private_list.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(List.objects.count(), 2)

    def test_add_book_to_list(self):
        # Test adding book to list (Happy Path)
        response = self.client.post(
            f'/api/v1/lists/{self.private_list.id}/books/',
            {'book_id': self.book1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookList.objects.count(), 1)

    def test_add_book_to_other_user_list(self):
        # Test adding book to other user's list (Security Case)
        response = self.client.post(
            f'/api/v1/lists/{self.other_user_list.id}/books/',
            {'book_id': self.book1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_books_in_list(self):
        # Test listing books in a list (Happy Path)
        BookList.objects.create(list=self.private_list, book=self.book1)
        BookList.objects.create(list=self.private_list, book=self.book2)
        response = self.client.get(
            f'/api/v1/lists/{self.private_list.id}/books/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_remove_book_from_list(self):
        # Test removing book from list (Happy Path)
        entry = BookList.objects.create(list=self.private_list, book=self.book1)
        response = self.client.delete(
            f'/api/v1/lists/{self.private_list.id}/books/',
            {'book_id': self.book1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(BookList.objects.filter(id=entry.id).exists())

    def test_remove_nonexistent_book(self):
        # Test removing non-existent book from list (Error Case)
        response = self.client.delete(
            f'/api/v1/lists/{self.private_list.id}/books/',
            {'book_id': 999}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_duplicate_book_to_list(self):
        # Test adding duplicate book to list (Error Case)
        BookList.objects.create(list=self.private_list, book=self.book1)
        response = self.client.post(
            f'/api/v1/lists/{self.private_list.id}/books/',
            {'book_id': self.book1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_book_to_nonexistent_list(self):
        # Test adding book to non-existent list (Error Case)
        response = self.client.post(
            '/api/v1/lists/999/books/',
            {'book_id': self.book1.id}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_books_in_private_list_unauthorized(self):
        # Test listing books in private list as unauthorized user (Security Case)
        BookList.objects.create(list=self.other_user_list, book=self.book1)
        response = self.client.get(
            f'/api/v1/lists/{self.other_user_list.id}/books/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ListFilterTests(TestCase):
    def setUp(self):
        # Initialize users and lists for filter tests
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
        List.objects.create(name='Public List 1', user=self.user1, is_public=True)
        List.objects.create(name='Private List 1', user=self.user1, is_public=False)
        List.objects.create(name='Public List 2', user=self.user2, is_public=True)
        List.objects.create(name='Private List 2', user=self.user2, is_public=False)
        self.factory = RequestFactory()

    def tearDown(self):
        # Clean up lists and users after tests
        List.objects.all().delete()
        User.objects.all().delete()

    def test_filter_by_user_id(self):
        # Test filtering lists by user ID
        request = self.factory.get('/?user={}'.format(self.user1.id))
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset).qs
        self.assertEqual(filtered.count(), 2)
        self.assertTrue(all(list.user == self.user1 for list in filtered))

    def test_filter_by_username(self):
        # Test filtering lists by username
        request = self.factory.get('/?username=user2')
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset).qs
        self.assertEqual(filtered.count(), 2)
        self.assertTrue(all(list.user.username == 'user2' for list in filtered))

    def test_filter_mine_authenticated(self):
        # Test 'mine' filter for authenticated user
        request = self.factory.get('/?mine=true')
        request.user = self.user1  # Simulate authenticated user
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset, request=request).qs
        self.assertEqual(filtered.count(), 2)
        self.assertTrue(all(list.user == self.user1 for list in filtered))

    def test_filter_by_is_public(self):
        # Test filtering lists by public/private status
        request = self.factory.get('/?is_public=true')
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset).qs
        self.assertEqual(filtered.count(), 2)
        self.assertTrue(all(list.is_public is True for list in filtered))

    def test_filter_invalid_user_id(self):
        # Test filtering with non-existent user ID
        request = self.factory.get('/?user=9999')
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset).qs
        self.assertEqual(filtered.count(), 0)

    def test_filter_non_existent_username(self):
        # Test filtering with non-existent username
        request = self.factory.get('/?username=nonexistent')
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset).qs
        self.assertEqual(filtered.count(), 0)

    def test_combined_filters(self):
        # Test combined filtering with multiple parameters
        request = self.factory.get(f'/?user={self.user1.id}&is_public=true')
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset).qs
        self.assertEqual(filtered.count(), 1)
        self.assertEqual(filtered[0].user, self.user1)
        self.assertTrue(filtered[0].is_public)

    def test_filter_mine_unauthenticated(self):
        # Test 'mine' filter for unauthenticated users should return empty set
        request = self.factory.get('/?mine=true')
        request.user = None  # Simulate unauthenticated user
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset, request=request).qs
        self.assertEqual(filtered.count(), 0)

    def test_user_data_separation(self):
        # Test ensuring separation of different users' data
        request = self.factory.get(f'/?user={self.user1.id}')
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset).qs
        self.assertFalse(any(list.user == self.user2 for list in filtered))

    def test_no_filter_parameters(self):
        # Test no filtering when parameters are absent
        request = self.factory.get('/')
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset).qs
        self.assertEqual(filtered.count(), 4)

    def test_invalid_filter_parameters(self):
        # Test invalid parameters should not affect results
        request = self.factory.get('/?invalid_param=value&unknown=123')
        queryset = List.objects.all()
        filtered = ListFilter(request.GET, queryset=queryset).qs
        self.assertEqual(filtered.count(), 4)