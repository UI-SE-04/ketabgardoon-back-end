from rest_framework import serializers
from .models import ReadingTarget

class ReadingTargetSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = ReadingTarget
        fields = ['id', 'year', 'target_books', 'read_books', 'progress_percentage']
        read_only_fields = ['id', 'year', 'read_books', 'progress_percentage']

    def validate_target_books(self, value):
        if value < 0:
            raise serializers.ValidationError("number of books cannot be negative")
        return value