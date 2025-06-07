from rest_framework import serializers
from lists.models import List
from .models import CustomUser
import secrets
from django.contrib.auth.password_validation import validate_password
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
            'password': {'write_only': True, 'required': False},
            'email': {'read_only': True},
            'id': {'read_only': True}
        }
    def validate_username(self, value):
        # safe request
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None

        # user is authenticated
        if user and user.is_authenticated:
            # user name not changed
            if user.username == value:
                return value
            # check duplication of new user name
            if CustomUser.objects.filter(username=value, is_temporary=False).exclude(id=user.id).exists():
                raise serializers.ValidationError("duplicate username")
        else:
            # for sign up
            if CustomUser.objects.filter(username=value, is_temporary=False).exists():
                raise serializers.ValidationError("duplicate username")
        return value
    def validate_password(self, value):
        if value:
            validate_password(value)
        return value
    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.first_name = validated_data.get('first_name', '')
        instance.last_name = validated_data.get('last_name', '')
        instance.is_private = validated_data.get('is_private', False)
        instance.image = validated_data.get('image', None)
        instance.bio = validated_data.get('bio', '')
        # update password for signup or when is needed
        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])
            if instance.is_temporary:
                instance.is_temporary = False
                instance.is_email_verified = True
                instance.email_verification_code = None
                instance.verification_code_expiry = None
                List.objects.create(name='خوانده شده', user=instance, is_default=True)
                List.objects.create(name='مورد علاقه', user=instance, is_default=True)
                List.objects.create(name='در حال خواندن', user=instance, is_default=True)
                List.objects.create(name='پیشنهادی', user=instance, is_default=True, is_public=True)
        instance.save()
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

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("wrong password")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value, is_temporary=False)
            if not user.is_email_verified:
                raise serializers.ValidationError("email is not verified")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("email does not exist")
        return value

    def save(self):
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)
        verification_code = ''.join(secrets.choice('0123456789') for _ in range(6))
        expiry_time = timezone.now() + timedelta(minutes=10)

        user.email_verification_code = verification_code
        user.verification_code_expiry = expiry_time
        user.save()

        send_mail(
            subject='بازیابی رمز عبور',
            message=f'کد بازیابی رمز عبور شما: {verification_code}\nاین کد تا 10 دقیقه معتبر است.\nکتابگردون',
            from_email='???',
            recipient_list=[email],
            fail_silently=False,
        )
        return user

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        verification_code = data.get('verification_code')

        try:
            user = CustomUser.objects.get(
                email=email,
                email_verification_code=verification_code,
                is_temporary=False
            )
            if user.verification_code_expiry < timezone.now():
                raise serializers.ValidationError("code is expired")
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("wrong code or email")

        validate_password(data['new_password'])
        return data

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = CustomUser.objects.get(email=email)
        user.set_password(new_password)
        user.email_verification_code = None
        user.verification_code_expiry = None
        user.save()
        return user