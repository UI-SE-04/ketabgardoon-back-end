from rest_framework import viewsets, permissions, serializers
from .models import Comment, UserCommentLike
from .serializers import CommentSerializer, UserCommentLikeSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    Supports list, retrieve, create, update, and destroy.
    """
    queryset = Comment.objects.select_related('user', 'book', 'reply_to').all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Ensures the `user` field is set from the authenticated user
        serializer.save(user=self.request.user)


class UserCommentLikeViewSet(viewsets.ModelViewSet):
    """
    Users can like or unlike comments.
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