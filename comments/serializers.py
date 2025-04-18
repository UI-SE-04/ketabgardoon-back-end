from rest_framework import serializers
from .models import Comment, UserCommentLike

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'book', 'comment_text', 'reply_to',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserCommentLikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = UserCommentLike
        fields = ['id', 'user', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
