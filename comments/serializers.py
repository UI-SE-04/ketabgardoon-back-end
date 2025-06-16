from rest_framework import serializers
from .models import Comment, UserCommentLike

class CommentSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    user_liked = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'book', 'comment_text', 'reply_to',
            'created_at', 'updated_at',
            'likes_count', 'user_liked', 'replies_count',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'likes_count', 'user_liked', 'replies_count']

    def get_likes_count(self, obj):
        # Count total likes on this comment
        return obj.likes.count()

    def get_user_liked(self, obj):
        # Check if the current user liked this comment
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False

    def get_replies_count(self, obj):
        # Count direct replies to this comment
        return obj.replies.count()

    def validate_reply_to(self, value):
        # Enforce only one level deep replies
        if value is not None and value.reply_to is not None:
            raise serializers.ValidationError(
                "You may only reply to top-level comments (one level of replies allowed)."
            )
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)

class UserCommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCommentLike
        fields = ['id', 'comment', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)