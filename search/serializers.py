from rest_framework import serializers
from books.models import Book, Author, Category
from custom_users.models import CustomUser

class BookSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'categories']

class AuthorSerializer(serializers.ModelSerializer):
    nationality = serializers.CharField(source='nationality.name', allow_null=True)

    class Meta:
        model = Author
        fields = ['id', 'name', 'nationality']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name']

class CategorySerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, source='book_set')

    class Meta:
        model = Category
        fields = ['id', 'title', 'books']