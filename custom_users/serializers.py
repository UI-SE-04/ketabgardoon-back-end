from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_private', 'image', 'bio', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}  # پسورد فقط برای نوشتن قابل مشاهده باشد
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_private=validated_data.get('is_private', False),
            image=validated_data.get('image', None),
            bio=validated_data.get('bio', '')
        )
        return user
