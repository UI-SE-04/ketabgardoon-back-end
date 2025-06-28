from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from countries.models import Country
from custom_users.models import CustomUser
from books.models import Author

class AuthorViewSetTestCase(APITestCase):
    def setUp(self):
        # Initialize admin, regular user, country, author, and JWT tokens for tests
        self.admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        self.user = CustomUser.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='userpass'
        )

        self.country = Country.objects.create(country='Iran', country_code='IR')
        self.author = Author.objects.create(
            name='Ahmad Mahmoud',
            nationality=self.country,
            bio='Contemporary Iranian author'
        )

        # Create JWT tokens
        self.admin_token = RefreshToken.for_user(self.admin).access_token
        self.user_token = RefreshToken.for_user(self.user).access_token

    def get_authenticated_client(self, token):
        # Set up client with provided JWT token for authenticated requests
        client = self.client
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        return client

    def test_list_authors_unauthenticated(self):
        # Test accessing the authors list without authentication
        url = reverse('author-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_author(self):
        # Test retrieving details of an author
        url = reverse('author-detail', args=[self.author.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Ahmad Mahmoud')

    def test_update_author_admin(self):
        # Test updating an author by admin
        client = self.get_authenticated_client(self.admin_token)
        url = reverse('author-detail', args=[self.author.id])
        data = {'bio': 'Updated biography'}
        response = client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.author.refresh_from_db()
        self.assertEqual(self.author.bio, 'Updated biography')

    def test_delete_author_admin(self):
        # Test deleting an author by admin
        client = self.get_authenticated_client(self.admin_token)
        url = reverse('author-detail', args=[self.author.id])
        response = client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Author.objects.count(), 0)

    def test_view_count_increment(self):
        # Test incrementing view count per visitor per day
        url = reverse('author-detail', args=[self.author.id])

        # First request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.author.refresh_from_db()
        initial_views = self.author.view_count

        # Second request from the same user (should not increment)
        response2 = self.client.get(url)
        self.author.refresh_from_db()
        self.assertEqual(self.author.view_count, initial_views)

        # Request from another user
        client2 = self.get_authenticated_client(self.user_token)
        response3 = client2.get(url)
        self.author.refresh_from_db()
        self.assertEqual(self.author.view_count, initial_views + 1)

    def test_search_authors(self):
        # Test searching authors by name
        Author.objects.create(name='Jalal Al Ahmad', bio='Author and critic')
        url = reverse('author-list')
        response = self.client.get(url, {'search': 'Jalal'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Jalal Al Ahmad')

    def test_sort_by_view_count(self):
        # Test sorting authors by view count
        author2 = Author.objects.create(name='Second Author', view_count=100)
        author3 = Author.objects.create(name='Third Author', view_count=50)

        url = reverse('author-list')
        response = self.client.get(url, {'sort': 'view'})
        results = response.data['results']

        self.assertEqual(results[0]['id'], author2.id)
        self.assertEqual(results[1]['id'], author3.id)
        self.assertEqual(results[2]['id'], self.author.id)

    def test_sort_by_rating(self):
        # Test sorting authors by rating
        # Create rating data for testing
        author2 = Author.objects.create(name='High Rated Author')
        # (Create books and ratings here)

        url = reverse('author-list')
        response = self.client.get(url, {'sort': 'rating'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify sorting correctness

    def test_retrieve_nonexistent_author(self):
        # Test retrieving a non-existent author
        url = reverse('author-detail', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_author_invalid_data(self):
        # Test updating author with invalid data
        client = self.get_authenticated_client(self.admin_token)
        url = reverse('author-detail', args=[self.author.id])
        data = {'birth_date': 'invalid-date'}
        response = client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class AuthorSecurityTestCase(APITestCase):
    def setUp(self):
        # Initialize admin, regular user, author, and JWT tokens for security tests
        self.admin = CustomUser.objects.create_superuser(
            username='admin',
            password='adminpass'
        )
        self.user = CustomUser.objects.create_user(
            username='user',
            password='userpass'
        )
        self.author = Author.objects.create(name='Test Author')

        self.admin_token = RefreshToken.for_user(self.admin).access_token
        self.user_token = RefreshToken.for_user(self.user).access_token

    def test_invalid_token_access(self):
        # Test accessing with an invalid JWT token
        client = self.client
        client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        url = reverse('author-list')
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)