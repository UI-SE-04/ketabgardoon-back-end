from django.urls import path

from rest_framework.routers import DefaultRouter
from authors.viewsets import AuthorViewSet, AuthorBooksView
from books.viewsets import PublisherViewSet, RoleViewSet, CategoryViewSet, StoreViewSet, BookAuthorViewSet, \
    BookISBNViewSet, BookStoreViewSet, BookViewSet
from countries.viewsets import CountryViewSet
# custom user may need refactoring
from custom_users.viewsets import UserViewSet, EmailSubmissionView, EmailVerificationView, UserCompletionView, \
    CustomTokenObtainPairView, ChangePasswordView, PasswordResetRequestView, PasswordResetConfirmView
from comments.viewsets import CommentViewSet, UserCommentLikeViewSet
from lists.viewsets import ListViewSet
from lists.views import IconViewSet
from rest_framework_simplejwt.views import TokenRefreshView

from search.views import CategorySearchView, SearchView

# (register other app viewsets here)

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
#router.register(r'countries', CountryViewSet, basename='nationality')

router.register(r'publishers', PublisherViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'book-authors', BookAuthorViewSet)
router.register(r'book-isbns', BookISBNViewSet)
router.register(r'book-stores', BookStoreViewSet)
router.register(r'books', BookViewSet)

router.register(r'nationalities', CountryViewSet, basename='nationality')
#router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'comment-likes', UserCommentLikeViewSet, basename='comment-like')

router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'comment-likes', UserCommentLikeViewSet, basename='commentlike')


router.register(r'lists', ListViewSet, basename='lists')

router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls


urlpatterns += [
    path('authors/<int:author_id>/books/', AuthorBooksView.as_view(), name='book-authors'),
    path('lists/icons/', IconViewSet.as_view(), name='icon-lists'),

    path('submit-email/', EmailSubmissionView.as_view(), name='submit-email'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('complete-registration/', UserCompletionView.as_view(), name='complete-registration'),

    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    path('category-search/', CategorySearchView.as_view(), name='category_search'),
    path('search/', SearchView.as_view(), name='search'),

]
