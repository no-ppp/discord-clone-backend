from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from .models import FriendRequest

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'password2', 'avatar', 'status']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "Hasła muszą być takie same"})

        try:
            validate_password(attrs.get('password'))
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def create(self, validated_data):
        # Usuwamy password2 z validated_data
        validated_data.pop('password2', None)
        
        # Tworzymy użytkownika z zaszyfrowanym hasłem
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Dodajemy pozostałe pola jeśli istnieją
        if 'avatar' in validated_data:
            user.avatar = validated_data['avatar']
        if 'status' in validated_data:
            user.status = validated_data['status']
        
        user.save()
        return user

    def update(self, instance, validated_data):
        # Jeśli aktualizujemy hasło
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        # Aktualizujemy pozostałe pola
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Hasła muszą być takie same!")
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'),
                              username=email,  # Twój model powinien obsługiwać logowanie przez email
                              password=password)
            
            if not user:
                raise serializers.ValidationError('Nieprawidłowy email lub hasło.')
            
            refresh = self.get_token(user)
            
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        
        raise serializers.ValidationError('Musisz podać email i hasło.') 

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Użytkownik o podanym adresie email nie istnieje")
        return value

    def save(self):
        user = self.user
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
        
        send_mail(
            'Reset hasła',
            f'Kliknij w link aby zresetować hasło: {reset_url}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    token = serializers.CharField()
    uidb64 = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Hasła muszą być takie same!")
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return data 

class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at'] 