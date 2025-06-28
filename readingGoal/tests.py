from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from django.contrib.auth import get_user_model
from jalali_date import date2jalali
from custom_users.models import CustomUser
from readingGoal.models import ReadingTarget

User = get_user_model()

class ReadingTargetTests(TestCase):
    def setUp(self):
        # Initialize user, client, and current Jalali year
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.current_year = date2jalali(timezone.now()).year
        self.url = '/api/v1/reading-target/'

    def tearDown(self):
        # Clean up database after each test
        ReadingTarget.objects.all().delete()
        CustomUser.objects.all().delete()

    def test_reading_target_view_get_success(self):
        # Test successful retrieval of current year's reading target
        target = ReadingTarget.objects.create(
            user=self.user,
            year=self.current_year,
            target_books=20
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['year'], self.current_year)
        self.assertEqual(response.data['target_books'], 20)
        self.assertEqual(response.data['progress_percentage'], 0.0)

    def test_reading_target_view_post_create_success(self):
        # Test successful creation of a new reading target
        data = {'target_books': 30}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['target_books'], 30)
        # Verify record creation in database
        target = ReadingTarget.objects.get(user=self.user)
        self.assertEqual(target.target_books, 30)

    def test_reading_target_view_post_update_success(self):
        # Test successful update of an existing reading target
        ReadingTarget.objects.create(
            user=self.user,
            year=self.current_year,
            target_books=15
        )
        data = {'target_books': 25}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['target_books'], 25)

    def test_reading_target_view_post_invalid_negative(self):
        # Test error when setting a negative target
        data = {'target_books': -5}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)

    def test_reading_target_view_post_invalid_type(self):
        # Test error when setting target with invalid data type
        data = {'target_books': 'abc'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('A valid integer is required', str(response.content))

    def test_reading_target_view_post_min_value(self):
        # Test successful setting of minimum valid value (zero)
        data = {'target_books': 0}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['target_books'], 0)

    def test_reading_target_view_post_max_value(self):
        # Test successful setting of maximum valid value
        data = {'target_books': 2147483647}  # Maximum IntegerField value
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['target_books'], 2147483647)

    def test_reading_target_view_previous_year(self):
        # Test automatic handling of previous years' targets
        past_year = self.current_year - 1
        ReadingTarget.objects.create(
            user=self.user,
            year=past_year,
            target_books=10
        )
        response = self.client.get(self.url)
        # Should return current year's target (not past year)
        self.assertEqual(response.data['year'], self.current_year)
        self.assertEqual(response.data['target_books'], 0)  # Default value

    def test_reading_target_view_unauthenticated(self):
        # Test lack of access without authentication
        self.client.logout()  # Log out user
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_reading_target_view_user_separation(self):
        # Test separation of different users' data
        user2 = CustomUser.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )
        ReadingTarget.objects.create(
            user=user2,
            year=self.current_year,
            target_books=50
        )
        # User1 should see their own target (not user2's)
        response = self.client.get(self.url)
        self.assertEqual(response.data['target_books'], 0)

    def test_progress_percentage_calculation(self):
        # Test correct calculation of progress percentage
        target = ReadingTarget.objects.create(
            user=self.user,
            year=self.current_year,
            target_books=10,
            read_books=3
        )
        response = self.client.get(self.url)
        self.assertEqual(response.data['progress_percentage'], 30.0)

    def test_100_percent_progress(self):
        # Test correct calculation of 100% progress
        target = ReadingTarget.objects.create(
            user=self.user,
            year=self.current_year,
            target_books=5,
            read_books=5
        )
        response = self.client.get(self.url)
        self.assertEqual(response.data['progress_percentage'], 100.0)

    def test_zero_target_progress(self):
        # Test correct handling of zero book target
        target = ReadingTarget.objects.create(
            user=self.user,
            year=self.current_year,
            target_books=0,
            read_books=3
        )
        response = self.client.get(self.url)
        self.assertEqual(response.data['progress_percentage'], 0.0)