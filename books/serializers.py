from rest_framework import serializers

from .models import (Book, Publisher, Category, Store,
                     Role, BookAuthor, BookISBN, BookStore,
                     Rating,
                     )


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'address', 'website', 'logo', 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'website', 'phone', 'logo']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'title']

class BookAuthorSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source='author.id')
    author_name = serializers.CharField(source='author.name')
    author_photo = serializers.ImageField(source='author.author_photo')
    author_role = serializers.CharField(source='role.title')
    class Meta:
        model = BookAuthor
        fields = ['author_id', 'author_name', 'author_photo', 'author_role']


class BookISBNSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookISBN
        fields = ['id', 'isbn']

class BookStoreSerializer(serializers.ModelSerializer):
    store = StoreSerializer()
    class Meta:
        model = BookStore
        fields = ['id', 'store', 'url']

class BookSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer(read_only=True)
    authors = BookAuthorSerializer(source='bookauthor_set', many=True, read_only=True, )
    categories = CategorySerializer(many=True, read_only=True)
    stores = BookStoreSerializer(source='bookstore_set', many=True, read_only=True)
    isbns = BookISBNSerializer(source='bookisbn_set', many=True, read_only=True)

    ratings_count = serializers.IntegerField(read_only=True)
    ratings_avg = serializers.FloatField(read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'summary', 'publisher', 'published_date',
            'cover', 'created_at', 'updated_at', 'authors', 'categories', 'stores',
            'isbns', 'view_count', 'ratings_count', 'ratings_avg'
        ]
        read_only_fields = ['id', 'view_count', 'ratings_count', 'ratings_avg', 'updated_at', 'created_at']


class BookIdListSerializer(serializers.Serializer):
    """
    Example output:
    {"book_ids": [1, 2, 3]}
    """
    book_ids = serializers.ListField(child=serializers.IntegerField())


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'book', 'user', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
