from rest_framework import serializers
from .models import Author
from books.models import BookAuthor

class AuthorSerializer(serializers.ModelSerializer):
    total_ratings = serializers.IntegerField()
    average_rating = serializers.FloatField()

    class Meta:
        model = Author
        fields = [
            'id', 'name', 'birth_date', 'death_date',
            'nationality', 'bio', 'author_photo', 'call_info',
            'created_at', 'updated_at', 'total_ratings',
            'average_rating', 'view_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_ratings',
            'average_rating', 'view_count', ]


class AuthorBookSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField(source='book.id')
    book_title = serializers.CharField(source='book.title')
    book_cover = serializers.ImageField(source='book.cover')
    role_title = serializers.CharField(source='role.title')

    class Meta:
        model = BookAuthor
        fields = ['book_id', 'book_title', 'book_cover', 'role_title']
