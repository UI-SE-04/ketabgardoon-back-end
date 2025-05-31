from rest_framework import serializers
from lists.models import List
from .models import CustomUser
import secrets
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta


class EmailSubmissionSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value, is_temporary=False).exists():
            raise serializers.ValidationError("این ایمیل قبلاً ثبت شده است.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))

        # check if temporary user exists
        user, created = CustomUser.objects.get_or_create(
            email=email,
            is_temporary=True,
            defaults={
                'username': f'temp_{email}_{timezone.now().timestamp()}',
                'email_verification_code': verification_code,
                'is_email_verified': False
            }
        )

        if not created:
            # create code and save
            user.email_verification_code = verification_code
            user.save()

        send_mail(
            subject='تأیید ایمیل',
            message=f'کد تأیید شما: {verification_code}',
            from_email='???',
            recipient_list=[email],
            fail_silently=False,
        )

        return user

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)
    def validate(self, data):
        email = data.get('email')
        verification_code = data.get('verification_code')

        try:
            user = CustomUser.objects.get(
                email=email,
                email_verification_code=verification_code,
                is_temporary=True
            )
            if user.is_email_verified:
                raise serializers.ValidationError("ایمیل قبلاً تأیید شده است.")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("ایمیل یا کد تأیید اشتباه است.")

        return data

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_private', 'image', 'bio', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
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
        List.objects.create(name='خوانده شده', user=user, is_default=True)
        List.objects.create(name='مورد علاقه', user=user, is_default=True)
        List.objects.create(name='در حال خواندن', user=user, is_default=True)
        List.objects.create(name='پیشنهادی', user=user, is_default=True, is_public=True)
        return user


