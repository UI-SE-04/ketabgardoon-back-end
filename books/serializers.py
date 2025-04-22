from rest_framework import serializers
from .models import Book, Publisher, Category, Store, Role, BookAuthor


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
