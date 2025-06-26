# serializers.py

from rest_framework import serializers
from .models import List, BookList
from books.models import Book


class IconField(serializers.Field):
    """
    A custom field which:
     - On input, accepts a plain filename (e.g. "xyz.png")
     - On output, returns the full URL (e.g. "/media/lists/icons/xyz.png")
    """
    def to_internal_value(self, data):
        # validate that the client actually sent a filename string
        if not isinstance(data, str):
            raise serializers.ValidationError('Icon filename must be a string.')
        return data  # this becomes validated_data['icon']

    def to_representation(self, value):
        # `value` here is the stored filename (e.g. "xyz.png")
        print(value)
        return List.get_icon_url(value)


class ListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    icon = IconField()  # single field for both read & write

    class Meta:
        model = List
        fields = ['id', 'name', 'user', 'is_default', 'is_public', 'icon', 'created_at']
        read_only_fields = ['id', 'user', 'is_default', 'created_at']


class BookInListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing books in a List.
    """
    book_id = serializers.IntegerField(source='book.id', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_cover = serializers.ImageField(source='book.cover', read_only=True)
    added_at = serializers.DateTimeField(read_only=True)
    authors = serializers.SerializerMethodField()
    class Meta:
        model = BookList
        fields = ['book_id', 'book_title', 'book_cover', 'authors', 'added_at']

    def get_authors(self, obj):
        return [ author.name for author in obj.book.authors.all() ]



class BookListCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for adding a book to a List.
    Only needs the book ID; the list is supplied by the view.
    """
    book_id = serializers.IntegerField(write_only=True)
    authors = serializers.SerializerMethodField()
    class Meta:
        model = BookList
        fields = ['book_id', 'authors']

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

    def get_authors(self, obj):
        return [ author.name for author in obj.book.authors.all() ]