from rest_framework.routers import DefaultRouter

from authors.viewsets import AuthorViewSet
from countries.viewsets import NationalityViewSet
from comments.viewsets import CommentViewSet, UserCommentLikeViewSet
# (register other app viewsets here)

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'nationalities', NationalityViewSet, basename='nationality')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'comment-likes', UserCommentLikeViewSet, basename='comment-like')
# e.g. router.register(r'books', BookViewSet)

urlpatterns = router.urls