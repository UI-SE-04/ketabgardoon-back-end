from rest_framework import serializers
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            'id', 'name', 'birth_date', 'nationality',
            'bio', 'author_photo', 'call_info',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
