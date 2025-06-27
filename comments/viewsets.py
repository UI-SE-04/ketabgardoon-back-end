from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Comment, UserCommentLike
from .serializers import CommentSerializer, UserCommentLikeSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    Supports list, retrieve, create, update, destroy,
    plus a `/comments/{id}/like/` endpoint for simple like actions.
    """
    queryset = Comment.objects.select_related('user', 'book', 'reply_to').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        # Filter by book ID
        book_id = params.get('book')
        if book_id:
            qs = qs.filter(book_id=book_id)
        # Filter by user ID
        user_id = params.get('user')
        if user_id:
            qs = qs.filter(user_id=user_id)
        # Filter by parent comment ID for replies
        replyto = params.get('replyto')
        if replyto:
            qs = qs.filter(reply_to_id=replyto)
        return qs

    def perform_create(self, serializer):
        # Ensures the `user` field is set from the authenticated user
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get', 'post', 'delete'], permission_classes=[permissions.IsAuthenticatedOrReadOnly],
            serializer_class=UserCommentLikeSerializer)
    def like(self, request, pk=None):
        """
        GET: return whether the user liked this comment and total likes
        POST: like the comment
        DELETE: unlike the comment
        """
        comment = get_object_or_404(Comment, pk=pk)
        user = request.user

        if request.method == 'GET':
            return Response({
                'likes_count': comment.likes.count(),
                'user_liked': comment.likes.filter(user=user).exists() if user.is_authenticated else False
            })

        if not user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        if request.method == 'POST':
            # Prevent duplicate likes
            obj, created = UserCommentLike.objects.get_or_create(comment=comment, user=user)
            if not created:
                return Response({'detail': 'Already liked.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Liked.'}, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            # Unlike the comment if exists
            deleted, _ = UserCommentLike.objects.filter(comment=comment, user=user).delete()
            if deleted:
                return Response({'detail': 'Unliked.'}, status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'No like to remove.'}, status=status.HTTP_400_BAD_REQUEST)


class UserCommentLikeViewSet(viewsets.ModelViewSet):
    """
    Supports list, retrieve, create, destroy of comment likes.
    """
    queryset = UserCommentLike.objects.select_related('user', 'comment').all()
    serializer_class = UserCommentLikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Prevent duplicate likes
        comment = serializer.validated_data['comment']
        user = self.request.user
        if UserCommentLike.objects.filter(comment=comment, user=user).exists():
            raise serializers.ValidationError("You have already liked this comment.")
        serializer.save(user=user)
