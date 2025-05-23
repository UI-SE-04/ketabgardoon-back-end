# serializers.py

from rest_framework import serializers
from .models import List, ListIcon, BookList
from books.models import Book


class ListIconSerializer(serializers.ModelSerializer):
    """
    Serializer for ListIcon: returns id and full URL to the image.
    """
    icon = serializers.ImageField(read_only=True)

    class Meta:
        model = ListIcon
        fields = ['id', 'icon']


class ListSerializer(serializers.ModelSerializer):
    """
    Serializer for List:
     - exposes icon URL (via the FK)
     - makes `user`, `is_default` and `created_at` read-only
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
    icon = serializers.ImageField(source='icon_id.icon', read_only=True)

    class Meta:
        model = List
        fields = [
            'id', 'name', 'user',
            'is_default', 'is_public',
            'icon', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'is_default', 'created_at']


class BookInListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing books in a List.
    """
    book_id = serializers.IntegerField(source='book.id', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_cover = serializers.ImageField(source='book.cover', read_only=True)
    added_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BookList
        fields = ['book_id', 'book_title', 'book_cover', 'added_at']


class BookListCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for adding a book to a List.
    Only needs the book ID; the list is supplied by the view.
    """
    book_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BookList
        fields = ['book_id']

    def validate_book_id(self, value):
        """
        Ensure the Book exists.
        """
        if not Book.objects.filter(id=value).exists():
            raise serializers.ValidationError("Book not found.")
        return value

    def create(self, validated_data):
        """
        Create the BookList entry, attaching it to the 'list' from context.
        """
        list_obj = self.context['list_obj']
        return BookList.objects.create(
            list=list_obj,
            book_id=validated_data['book_id']
        )
