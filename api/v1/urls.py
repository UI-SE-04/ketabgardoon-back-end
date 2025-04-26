from django.urls import path

from rest_framework.routers import DefaultRouter
from authors.viewsets import AuthorViewSet, AuthorBooksView
from books.viewsets import PublisherViewSet, RoleViewSet, CategoryViewSet, StoreViewSet, BookAuthorViewSet, \
    BookISBNViewSet, BookStoreViewSet, BookViewSet
from countries.viewsets import CountryViewSet
from custom_users.viewsets import UserViewSet

# (register other app viewsets here)

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'countries', CountryViewSet, basename='nationality')
 

router.register(r'publishers', PublisherViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'book-authors', BookAuthorViewSet)
router.register(r'book-isbns', BookISBNViewSet)
router.register(r'book-stores', BookStoreViewSet)
router.register(r'books', BookViewSet)
 
# e.g. router.register(r'books', BookViewSet)
router.register(r'users', UserViewSet, basename='user')

 

urlpatterns = router.urls

urlpatterns += [
    path('authors/<int:author_id>/books/', AuthorBooksView.as_view(), name='book-authors'),
]