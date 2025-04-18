from rest_framework import serializers
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'id', 'name', 'birth_date', 'nationality',
            'rating', 'total_sum_of_ratings', 'total_number_of_ratings',
            'bio', 'author_photo', 'call_info',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['rating', 'created_at', 'updated_at']
