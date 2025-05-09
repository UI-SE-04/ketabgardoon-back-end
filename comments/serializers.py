from rest_framework import serializers
from .models import Comment, UserCommentLike

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'book',
            'comment_text',
            'reply_to',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_reply_to(self, value):
        """
        Enforces that replies are only one level deep:
            if `reply_to` is set, the parent comment must not itself be a reply.
        """
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
        fields = [
            'id',
            'comment',
            'user',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)