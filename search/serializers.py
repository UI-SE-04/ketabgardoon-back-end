from rest_framework import serializers
from books.models import Book, Author, Category
from custom_users.models import CustomUser

class BookSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)
    categories = serializers.StringRelatedField(many=True)
    ratings_count = serializers.IntegerField(read_only=True)
    ratings_avg = serializers.FloatField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'categories', 'ratings_count', 'ratings_avg']
        read_only_fields = ['ratings_count', 'ratings_avg']

class AuthorSerializer(serializers.ModelSerializer):
    nationality = serializers.CharField(source='nationality.name', allow_null=True)
    total_ratings = serializers.IntegerField()
    average_rating = serializers.FloatField()
    author_photo = serializers.ImageField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'nationality', 'total_ratings', 'average_rating', 'author_photo']
        read_only_fields = ['total_ratings', 'average_rating']

class UserSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(allow_null=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'image']

class CategorySerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, source='book_set')

    class Meta:
        model = Category
        fields = ['id', 'title', 'books']