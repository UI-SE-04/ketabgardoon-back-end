from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from custom_users.models import CustomUser
from books.models import Book
from comments.models import Comment, UserCommentLike

User = get_user_model()

class UserCommentLikeModelTests(TestCase):
    def setUp(self):
        # Initialize users, book, and comment for tests
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
        self.book = Book.objects.create(title='Test Book')
        self.comment = Comment.objects.create(
            user=self.user,
            book=self.book,
            comment_text='Test comment'
        )

    def test_create_like_success(self):
        # Test successful creation of a like (Happy Path)
        like = UserCommentLike.objects.create(
            comment=self.comment,
            user=self.user
        )
        self.assertEqual(like.comment, self.comment)
        self.assertEqual(like.user, self.user)

    def test_duplicate_like(self):
        # Test creating a duplicate like (should fail) (Error Case)
        UserCommentLike.objects.create(comment=self.comment, user=self.user)
        with self.assertRaises(Exception):
            UserCommentLike.objects.create(comment=self.comment, user=self.user)

    def test_multiple_users_like(self):
        # Test multiple users liking the same comment (Edge Case)
        UserCommentLike.objects.create(comment=self.comment, user=self.user)
        UserCommentLike.objects.create(comment=self.comment, user=self.other_user)
        self.assertEqual(self.comment.likes.count(), 2)

class CommentViewSetTests(APITestCase):
    def setUp(self):
        # Initialize users, book, comments, and like for tests
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

        self.book = Book.objects.create(
            title='Test Book',
            description='Test Description'
        )

        self.comment1 = Comment.objects.create(
            user=self.user1,
            book=self.book,
            comment_text='Top-level comment'
        )

        self.comment2 = Comment.objects.create(
            user=self.user2,
            book=self.book,
            comment_text='Reply comment',
            reply_to=self.comment1
        )

        self.like = UserCommentLike.objects.create(
            comment=self.comment1,
            user=self.user2
        )

    def test_create_comment_happy_path(self):
        # Test creating a new comment successfully (Happy Path)
        self.client.force_authenticate(user=self.user1)
        data = {
            'book': self.book.id,
            'comment_text': 'New comment'
        }
        response = self.client.post('/api/v1/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)

    def test_create_reply_happy_path(self):
        # Test creating a reply to a comment successfully (Happy Path)
        self.client.force_authenticate(user=self.user1)
        data = {
            'book': self.book.id,
            'comment_text': 'Reply to comment',
            'reply_to': self.comment1.id
        }
        response = self.client.post('/api/v1/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reply_to'], self.comment1.id)

    def test_create_comment_unauthenticated(self):
        # Test creating a comment without authentication (Access Error)
        data = {
            'book': self.book.id,
            'comment_text': 'Unauthenticated comment'
        }
        response = self.client.post('/api/v1/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_nested_reply_error(self):
        # Test creating a reply to a reply (Validation Error)
        self.client.force_authenticate(user=self.user1)
        data = {
            'book': self.book.id,
            'comment_text': 'Nested reply',
            'reply_to': self.comment2.id  # comment2 is already a reply
        }
        response = self.client.post('/api/v1/comments/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('only reply to top-level comments', str(response.content))

    def test_update_comment_happy_path(self):
        # Test updating a comment by its owner successfully
        self.client.force_authenticate(user=self.user1)
        data = {'comment_text': 'Updated comment text'}
        response = self.client.patch(f'/api/v1/comments/{self.comment1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg=f"Expected 200, got {response.status_code}. Response: {response.data}")
        self.comment1.refresh_from_db()
        self.assertEqual(self.comment1.comment_text, 'Updated comment text')


    def test_delete_comment_happy_path(self):
        # Test deleting a comment by its owner successfully
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/v1/comments/{self.comment1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment1.id).exists())

    def test_like_comment_happy_path(self):
        # Test liking a comment successfully (Happy Path)
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/v1/comments/{self.comment1.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(UserCommentLike.objects.filter(
            comment=self.comment1,
            user=self.user1
        ).exists())

    def test_unlike_comment_happy_path(self):
        # Test unliking a comment successfully (Happy Path)
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/v1/comments/{self.comment1.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserCommentLike.objects.filter(
            comment=self.comment1,
            user=self.user2
        ).exists())

    def test_duplicate_like_error(self):
        # Test creating a duplicate like (Validation Error)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/v1/comments/{self.comment1.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Already liked', str(response.content))

    def test_like_unauthenticated(self):
        # Test liking a comment without authentication (Access Error)
        response = self.client.post(f'/api/v1/comments/{self.comment1.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_comment_details_happy_path(self):
        # Test retrieving comment details successfully
        response = self.client.get(f'/api/v1/comments/{self.comment1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.comment1.id)
        self.assertEqual(response.data['likes_count'], 1)
        self.assertEqual(response.data['replies_count'], 1)

    def test_get_comments_list_happy_path(self):
        # Test retrieving the list of comments successfully
        response = self.client.get('/api/v1/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_comments_by_book(self):
        # Test filtering comments by book
        response = self.client.get(f'/api/v1/comments/?book={self.book.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_comments_by_user(self):
        # Test filtering comments by user
        response = self.client.get(f'/api/v1/comments/?user={self.user1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.user1.id)

    def test_comment_brute_force_protection(self):
        # Test brute force protection with rate limiting
        # TODO: Implement test using throttle classes
        pass