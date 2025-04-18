from rest_framework.routers import DefaultRouter
from authors.viewsets import AuthorViewSet
from countries.viewsets import CountryViewSet
# (register other app viewsets here)

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'countries', CountryViewSet, basename='country')
# e.g. router.register(r'books', BookViewSet)

urlpatterns = router.urls