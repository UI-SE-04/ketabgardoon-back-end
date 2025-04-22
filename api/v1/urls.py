from rest_framework.routers import DefaultRouter
from authors.viewsets import AuthorViewSet
from countries.viewsets import CountryViewSet
from custom_users.viewsets import UserViewSet

# (register other app viewsets here)

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'countries', CountryViewSet, basename='nationality')
# e.g. router.register(r'books', BookViewSet)
router.register(r'users', UserViewSet, basename='user')


urlpatterns = router.urls