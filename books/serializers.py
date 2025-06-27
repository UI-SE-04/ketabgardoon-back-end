from urllib.parse import urljoin

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers

from ketabgardoon.settings import MEDIA_URL
from .models import (Book, Publisher, Category, Store,
                     Role, BookAuthor, BookISBN, BookStore,
                     Rating,
                     )
from .stores import STORES, build_search_url


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
    # stores = BookStoreSerializer(source='bookstore_set', many=True, read_only=True)
    isbns = BookISBNSerializer(source='bookisbn_set', many=True, read_only=True)

    ratings_count = serializers.IntegerField(read_only=True)
    ratings_avg = serializers.FloatField(read_only=True)

    stores = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'summary', 'publisher', 'published_date',
            'cover', 'created_at', 'updated_at', 'authors', 'categories', 'stores',
            'isbns', 'view_count', 'ratings_count', 'ratings_avg', 'stores','page_count'
        ]
        read_only_fields = ['id', 'view_count', 'ratings_count', 'ratings_avg',
                            'updated_at', 'created_at', 'stores',]

    def get_stores(self, obj: Book):
        """
        For each configured store, build a dict with its name, logo URL,
        and a fully‐formed search URL for this book's title.
        """
        term = obj.title
        request = self.context.get('request')
        result = []

        for store in STORES:
            # Build the search URL
            url = build_search_url(store, term)

            # Construct the logo path under MEDIA_URL
            # e.g. "/media/online_bookstore_logo/taaghche.png"
            relative_logo = urljoin(
                settings.MEDIA_URL,
                f"online_bookstore_logo/{store['logo']}"
            )

            # If we have the request, turn it into an absolute URL
            if request is not None:
                logo_url = request.build_absolute_uri(relative_logo)
            else:
                logo_url = relative_logo

            result.append({
                'name': store['name'],
                'logo': logo_url,
                'url': url,
            })

        return result


class BookIdListSerializer(serializers.Serializer):
    """
    Example output:
    {"book_ids": [1, 2, 3]}
    """
    book_ids = serializers.ListField(child=serializers.IntegerField())


class RatingSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(5.0)  # Adjust max value as needed
        ]
    )
    class Meta:
        model = Rating
        fields = ['id', 'book', 'user', 'rating', 'created_at', 'updated_at']
        read_only_fields = ['id', 'book', 'user', 'created_at', 'updated_at']

