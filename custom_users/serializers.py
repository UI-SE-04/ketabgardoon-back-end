from rest_framework import serializers
from lists.models import List
from .models import CustomUser
import secrets
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

class EmailSubmissionSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value, is_temporary=False).exists():
            raise serializers.ValidationError("email already exists")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))
        expiry_time = timezone.now() + timedelta(minutes=10)  #expires after 10 mins
        # check if temporary user exists
        user, created = CustomUser.objects.get_or_create(
            email=email,
            is_temporary=True,
            defaults={
                'username': f'temp_{email}_{timezone.now().timestamp()}',
                'email_verification_code': verification_code,
                'verification_code_expiry': expiry_time,
                'is_email_verified': False
            }
        )
        if not created:
            # create code and save
            user.email_verification_code = verification_code
            user.verification_code_expiry = expiry_time
            user.save()

        send_mail(
            subject='تأیید ایمیل',
            message=f'کد تأیید شما: {verification_code} \nاین کد تا 10 دقیقه معتبر است\nکتابگردون ',
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
                raise serializers.ValidationError("email has already been verified.")
            if user.verification_code_expiry < timezone.now():
                raise serializers.ValidationError("code is expired")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("wrong email or code")

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
    def validate_username(self, value):
        if CustomUser.objects.filter(username=value, is_temporary=False).exists():
            raise serializers.ValidationError("this username is duplicated")
        return value
    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.set_password(validated_data.get('password',''))
        instance.first_name = validated_data.get('first_name', '')
        instance.last_name = validated_data.get('last_name', '')
        instance.is_private = validated_data.get('is_private', False)
        instance.image = validated_data.get('image', None)
        instance.bio = validated_data.get('bio', '')
        instance.is_temporary = False
        instance.is_email_verified = True
        instance.email_verification_code = None
        instance.verification_code_expiry = None
        instance.save()

        List.objects.create(name='خوانده شده', user=instance, is_default=True)
        List.objects.create(name='مورد علاقه', user=instance, is_default=True)
        List.objects.create(name='در حال خواندن', user=instance, is_default=True)
        List.objects.create(name='پیشنهادی', user=instance, is_default=True, is_public=True)
        return instance


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'username'  # main feature
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                raise serializers.ValidationError("wrong username or password")
            if not user.is_email_verified:
                raise serializers.ValidationError("your email is not verified")
            if user.is_temporary:
                raise serializers.ValidationError("temporary account can't login")

        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
        }
        return data