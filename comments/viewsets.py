from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Comment, UserCommentLike
from .serializers import CommentSerializer, UserCommentLikeSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('user', 'book', 'reply_to')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['book', 'user']
    search_fields = ['comment_text']
    ordering_fields = ['created_at', 'updated_at']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        comment = self.get_object()
        replies = Comment.objects.filter(reply_to=comment)
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)


class UserCommentLikeViewSet(viewsets.ModelViewSet):
    queryset = UserCommentLike.objects.all().select_related('user', 'comment')
    serializer_class = UserCommentLikeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['comment', 'user']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)