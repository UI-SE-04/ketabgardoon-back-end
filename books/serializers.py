from rest_framework import serializers
from .models import Book, Publisher, Category, Store, Role, BookAuthor, BookISBN, BookStore
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
    author = serializers.StringRelatedField()
    role = RoleSerializer()
    class Meta:
        model = BookAuthor
        fields = ['id', 'author', 'role', 'added_at']

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
    authors = BookAuthorSerializer(source='bookauthor_set', many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    stores = BookStoreSerializer(source='bookstore_set', many=True, read_only=True)
    isbns = BookISBNSerializer(source='bookisbn_set', many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'summary', 'publisher', 'published_date',
            'cover', 'created_at', 'updated_at', 'authors', 'categories', 'stores', 'isbns'
        ]