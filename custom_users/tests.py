from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from datetime import timedelta
import json
from custom_users.models import CustomUser
from lists.models import List
from books.models import Book, Publisher, Author, Category, Rating
from books.serializers import BookSerializer

User = get_user_model()

class UserCompletionTests(TestCase):
    def setUp(self):
        # Initialize API client, URL, and temporary user with verification code
        self.client = APIClient()
        self.url = '/api/v1/complete-registration/'
        self.user = CustomUser.objects.create(
            email='temp@example.com',
            is_temporary=True,
            email_verification_code='123456',
            verification_code_expiry=timezone.now() + timezone.timedelta(minutes=10),
            is_email_verified=False
        )
        self.verify_email()

    def verify_email(self):
        # Helper function to verify email before completion
        verify_url = '/api/v1/verify-email/'
        data = {
            'email': self.user.email,
            'verification_code': self.user.email_verification_code
        }
        response = self.client.post(verify_url, data)
        if response.status_code == 200:
            self.user.refresh_from_db()
        return response.status_code == 200

    def test_complete_signup_success(self):
        # Test successful completion of signup (Happy Path)
        data = {
            'email': self.user.email,
            'username': 'newuser',
            'password': 'StrongPass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200,
                         f"Expected 200, got {response.status_code}. Content: {response.content}")

        # Get updated user from database
        updated_user = CustomUser.objects.get(email=self.user.email)
        self.assertFalse(updated_user.is_temporary)
        self.assertEqual(updated_user.username, 'newuser')
        self.assertTrue(updated_user.check_password('StrongPass123!'))

        # Verify default lists created
        self.assertEqual(List.objects.filter(user=updated_user, is_default=True).count(), 4)
        self.assertIn('user', response.data)

    def test_duplicate_username(self):
        # Test using a duplicate username (Error Case)
        CustomUser.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='password123',
            is_temporary=False
        )
        data = {
            'email': self.user.email,
            'username': 'existing',  # Duplicate username
            'password': 'StrongPass123!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('A user with that username already exists', str(response.content))

    def test_weak_password(self):
        # Test using a weak password (Error Case)
        data = {
            'email': self.user.email,
            'username': 'newuser',
            'password': 'weak'  # Weak password
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('This password is too short', str(response.content))

    def test_missing_required_fields(self):
        # Test missing required fields (Edge Case)
        data = {
            'email': self.user.email,
            'username': 'newuser'
            # Missing password intentionally
        }
        response = self.client.post(self.url, data)

        # Advanced debugging
        print(f"\n{'=' * 50}")
        print("Missing fields test debug:")
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content}")

        try:
            content_json = json.loads(response.content.decode('utf-8'))
            print("JSON Response:", json.dumps(content_json, indent=2))
        except json.JSONDecodeError:
            print("Response is not JSON:", response.content.decode('utf-8'))

        # Get updated user from database
        updated_user = CustomUser.objects.get(email=self.user.email)
        print(f"User status: is_temporary={updated_user.is_temporary}")

        # Flexible assertion logic
        if response.status_code == 200:
            self.assertTrue(updated_user.is_temporary,
                            "User should remain temporary after incomplete registration")
            self.assertTrue(updated_user.is_temporary, "User should still be temporary")
        elif response.status_code == 400:
            self.assertIn('password', str(response.content))
        else:
            self.fail(f"Unexpected status code: {response.status_code}")

class EmailSubmissionTests(TestCase):
    def setUp(self):
        # Initialize API client and URL for email submission tests
        self.client = APIClient()
        self.url = '/api/v1/submit-email/'

    def test_submit_new_email_success(self):
        # Test successful submission of a new email (Happy Path)
        response = self.client.post(self.url, {'email': 'new@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomUser.objects.filter(email='new@example.com', is_temporary=True).exists())
        self.assertIn('email', response.data)

    def test_submit_existing_permanent_email(self):
        # Test submitting an existing permanent email (Error Case)
        CustomUser.objects.create(email='existing@example.com', is_temporary=False)
        response = self.client.post(self.url, {'email': 'existing@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('email already exists', str(response.content))

    def test_submit_invalid_email_format(self):
        # Test submitting an invalid email format (Edge Case)
        response = self.client.post(self.url, {'email': 'invalid-email'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Enter a valid email address', str(response.content))

    def test_resend_to_temporary_user(self):
        # Test resending code to a temporary user (Happy Path)
        user = CustomUser.objects.create(email='temp@example.com', is_temporary=True)
        initial_code = user.email_verification_code
        response = self.client.post(self.url, {'email': 'temp@example.com'})
        user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(initial_code, user.email_verification_code)

    def test_submit_empty_email(self):
        # Test submitting an empty email (Edge Case)
        response = self.client.post(self.url, {'email': ''})
        self.assertEqual(response.status_code, 400)
        self.assertIn('This field may not be blank', str(response.content))

class EmailVerificationTests(TestCase):
    def setUp(self):
        # Initialize API client, URL, and user for email verification tests
        self.client = APIClient()
        self.url = '/api/v1/verify-email/'
        self.user = CustomUser.objects.create(
            email='test@example.com',
            is_temporary=True,
            email_verification_code='123456',
            verification_code_expiry=timezone.now() + timedelta(minutes=10)
        )

    def test_verify_code_success(self):
        # Test successful verification of correct code (Happy Path)
        data = {'email': 'test@example.com', 'verification_code': '123456'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.data)

    def test_verify_expired_code(self):
        # Test verification of expired code (Error Case)
        self.user.verification_code_expiry = timezone.now() - timedelta(minutes=1)
        self.user.save()
        data = {'email': 'test@example.com', 'verification_code': '123456'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('code is expired', str(response.content))

    def test_verify_wrong_code(self):
        # Test verification with incorrect code (Error Case)
        data = {'email': 'test@example.com', 'verification_code': 'wrong'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('wrong email or code', str(response.content))

    def test_verify_already_verified(self):
        # Test verification of already verified email (Edge Case)
        self.user.is_email_verified = True
        self.user.save()
        data = {'email': 'test@example.com', 'verification_code': '123456'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('email has already been verified', str(response.content))

    def test_verify_non_existent_email(self):
        # Test verification with non-existent email (Security Case)
        data = {'email': 'nonexistent@example.com', 'verification_code': '123456'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('wrong email or code', str(response.content))

class AuthenticationTests(TestCase):
    def setUp(self):
        # Initialize API client, URL, and user for authentication tests
        self.client = APIClient()
        self.url = '/api/v1/login/'
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!',
            is_email_verified=True
        )

    def test_login_success(self):
        # Test successful login (Happy Path)
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_unverified_email(self):
        # Test login with unverified email (Security Case)
        self.user.is_email_verified = False
        self.user.save()
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('your email is not verified', str(response.content))

    def test_login_wrong_password(self):
        # Test login with incorrect password (Error Case)
        response = self.client.post(self.url, {
            'username': 'testuser',
            'password': 'WrongPass!'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('wrong username or password', str(response.content))

    def test_login_temporary_account(self):
        # Test login with temporary account (Security Case)
        temp_user = CustomUser.objects.create(
            email='temp@example.com',
            is_temporary=True,
            is_email_verified=True
        )
        response = self.client.post(self.url, {
            'username': temp_user.email,
            'password': 'any'
        })
        self.assertEqual(response.status_code, 400)

class PasswordChangeTests(TestCase):
    def setUp(self):
        # Initialize API client, URL, user, and token for password change tests
        self.client = APIClient()
        self.url = '/api/v1/change-password/'
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='old_password'
        )
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_successful_password_change(self):
        # Test successful password change (Happy Path)
        data = {
            'old_password': 'old_password',
            'new_password': 'New_Strong_Pass123!'
        }
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(check_password('New_Strong_Pass123!', self.user.password))

    def test_wrong_old_password(self):
        # Test submitting incorrect old password (Error Case)
        data = {
            'old_password': 'wrong_old_password',
            'new_password': 'New_Strong_Pass123!'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('wrong password', str(response.content))

    def test_weak_new_password(self):
        # Test submitting weak new password (Error Case)
        data = {
            'old_password': 'old_password',
            'new_password': 'weak'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('This password is too short', str(response.content))

    def test_unauthenticated_access(self):
        # Test access without authentication (Security Case)
        self.client.credentials()  # Remove auth
        data = {'old_password': 'any', 'new_password': 'any'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 401)

class PasswordResetTests(TestCase):
    def setUp(self):
        # Initialize API client, URLs, and user for password reset tests
        self.client = APIClient()
        self.request_url = '/api/v1/password-reset/request/'
        self.confirm_url = '/api/v1/password-reset/confirm/'
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='old_password',
            is_email_verified=True
        )

    def test_successful_password_reset_flow(self):
        # Test complete password reset flow (Happy Path)
        # Step 1: Request reset
        response = self.client.post(self.request_url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        reset_code = self.user.email_verification_code

        # Step 2: Confirm reset
        data = {'email': 'test@example.com', 'verification_code': reset_code}
        response = self.client.post(self.confirm_url, data)
        self.assertEqual(response.status_code, 200)

        # Verify new password
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(reset_code))

    def test_reset_unverified_email(self):
        # Test requesting reset for unverified email (Security Case)
        self.user.is_email_verified = False
        self.user.save()
        response = self.client.post(self.request_url, {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('email is not verified', str(response.content))

    def test_reset_nonexistent_email(self):
        # Test requesting reset for non-existent email (Error Case)
        response = self.client.post(self.request_url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('email does not exist', str(response.content))

    def test_confirm_expired_code(self):
        # Test confirming expired code (Error Case)
        self.client.post(self.request_url, {'email': 'test@example.com'})
        self.user.refresh_from_db()
        self.user.verification_code_expiry = timezone.now() - timedelta(minutes=1)
        self.user.save()
        data = {'email': 'test@example.com', 'verification_code': self.user.email_verification_code}
        response = self.client.post(self.confirm_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('code is expired', str(response.content))

    def test_confirm_wrong_code(self):
        # Test confirming incorrect code (Error Case)
        self.client.post(self.request_url, {'email': 'test@example.com'})
        data = {'email': 'test@example.com', 'verification_code': 'WRONG_CODE'}
        response = self.client.post(self.confirm_url, data)
        self.assertEqual(response.status_code, 400)

class UserViewSetTests(APITestCase):
    def setUp(self):
        # Initialize users and lists for user viewset tests
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123',
            is_private=False
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123',
            is_private=True
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        List.objects.create(name='Read', user=self.user1, is_default=True)
        List.objects.create(name='Favorites', user=self.user1, is_default=True)

    def test_retrieve_own_profile_happy_path(self):
        # Test retrieving own profile (Happy Path)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/v1/users/{self.user1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')

    def test_me_endpoint_happy_path(self):
        # Test using the /me endpoint (Happy Path)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user1.id)

    def test_update_other_profile_error(self):
        # Test updating another user's profile (Access Error)
        self.client.force_authenticate(user=self.user1)
        data = {'first_name': 'Unauthorized'}
        response = self.client.patch(f'/api/v1/users/{self.user2.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_list_users_happy_path(self):
        # Test listing users by admin (Happy Path)
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_admin_delete_user_happy_path(self):
        # Test deleting a user by admin (Happy Path)
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/v1/users/{self.user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user2.id).exists())

    def test_create_user_duplicate_username_error(self):
        # Test creating a user with a duplicate username (Validation Error)
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'user1',
            'email': 'new@example.com',
            'password': 'newpassword'
        }
        response = self.client.post('/api/v1/users/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('A user with that username already exists.', str(response.content))

    def test_update_password_via_profile_error(self):
        # Test changing password via profile (Unauthorized Error)
        self.client.force_authenticate(user=self.user1)
        data = {'password': 'newpassword'}
        response = self.client.patch(f'/api/v1/users/{self.user1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)