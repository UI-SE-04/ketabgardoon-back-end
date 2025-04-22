from rest_framework import serializers
from .models import Book, Publisher

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'address', 'website', 'logo', 'created_at', 'updated_at']
