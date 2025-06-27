from rest_framework import serializers
from books.models import Book, Author, Category
from custom_users.models import CustomUser
from django.db.models import Count, Avg

# Helper function to calculate ratings for books and authors
def get_ratings(obj, model_type='book'):
    """
    Calculate total ratings and average rating for a book or author.
    Args:
        obj: Book or Author instance
        model_type: 'book' or 'author'
    Returns:
        Tuple of (total_ratings, average_rating)
    """
    if model_type == 'book':
        ratings = obj.rating_set.aggregate(
            total_ratings=Count('id'),
            avg_rating=Avg('rating')
        )
    elif model_type == 'author':
        ratings = Book.objects.filter(
            bookauthor__author=obj
        ).aggregate(
            total_ratings=Count('rating'),
            avg_rating=Avg('rating__rating')
        )
    total_ratings = ratings['total_ratings'] or 0
    avg_rating = ratings['avg_rating'] or 0.0
    return total_ratings, avg_rating

class BookSerializer(serializers.ModelSerializer):
    authors = serializers.StringRelatedField(many=True)
    categories = serializers.StringRelatedField(many=True)
    ratings_count = serializers.SerializerMethodField()
    ratings_avg = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'title', 'authors', 'categories', 'ratings_count', 'ratings_avg']
        read_only_fields = ['ratings_count', 'ratings_avg']

    # ADDED: Methods for ratings_count and ratings_avg
    def get_ratings_count(self, obj):
        total_ratings, _ = get_ratings(obj, model_type='book')
        return total_ratings

    def get_ratings_avg(self, obj):
        _, avg_rating = get_ratings(obj, model_type='book')
        return avg_rating

class AuthorSerializer(serializers.ModelSerializer):
    nationality = serializers.CharField(source='nationality.name', allow_null=True)
    author_photo = serializers.ImageField()
    total_ratings = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'nationality', 'average_rating', 'author_photo', 'total_ratings']
        read_only_fields = ['total_ratings', 'average_rating']

    def get_total_ratings(self, obj):
        total_ratings, _ = get_ratings(obj, model_type='author')
        return total_ratings

    def get_average_rating(self, obj):
        _, avg_rating = get_ratings(obj, model_type='author')
        return avg_rating

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