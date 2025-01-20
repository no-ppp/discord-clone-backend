from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import FriendRequest, Notification, Friendship
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_spectacular.utils import extend_schema_field
from django.db.models import CharField
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

User = get_user_model()

# Podstawowy serializer do wyświetlania danych użytkownika
class BaseUserSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    @extend_schema_field(CharField())
    def get_username(self, obj) -> str:
        return obj.username or obj.email.split('@')[0]

class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username','bio', 'avatar', 'status', 'is_online']
        read_only_fields = ['id', 'email']

# Serializer do rejestracji
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'avatar', 'status']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "Hasła muszą być takie same"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        email = validated_data.get('email')
        validated_data['username'] = email
        return User.objects.create_user(**validated_data)

# Serializer do znajomych
class FriendSerializer(BaseUserSerializer):
    is_online = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'avatar', 'status', 'is_online']

# Serializer do zaproszeń do znajomych
class FriendRequestSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at', 'is_read']
        read_only_fields = ['id', 'created_at']

# Serializer do resetu hasła (jeśli potrzebujesz)
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Użytkownik o podanym adresie email nie istnieje")
        return value  

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate(email=email, password=password)
        
        if not user:
            raise serializers.ValidationError('Nieprawidłowy email lub hasło.')
        
        refresh = RefreshToken.for_user(user)
        return {
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username or user.email.split('@')[0],
                'avatar': user.avatar.url if user.avatar else None,
                'status': user.status,
                'is_online': True,
                'last_online': user.last_online
            }
        }

class FriendshipStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    since = serializers.DateTimeField(required=False)
    last_updated = serializers.DateTimeField(required=False)
    is_blocked = serializers.BooleanField()
    blocked_by = serializers.IntegerField(allow_null=True)

    def to_representation(self, instance):
        if isinstance(instance, Friendship):
            return {
                'status': instance.status,
                'since': instance.created_at,
                'last_updated': instance.updated_at,
                'is_blocked': instance.status == 'blocked',
                'blocked_by': instance.blocked_by.id if instance.blocked_by else None
            }
        return {
            'status': 'not_friends',
            'is_blocked': False
        }  

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, data):
        try:
            refresh_token = data.get('refresh_token')
            print(f"Próba walidacji tokenu: {refresh_token[:20]}...") # Debug
            
            try:
                token = RefreshToken(refresh_token)
                # Pobierz użytkownika
                user_id = token.payload.get('user_id')
                user = User.objects.get(id=user_id)
                print(f"Token poprawny, użytkownik: {user.email}") # Debug
                
                user.save()
                
                return data
                
            except TokenError as e:
                print(f"Błąd tokenu: {str(e)}") # Debug
                raise serializers.ValidationError("Nieprawidłowy token")
            except User.DoesNotExist:
                print("Nie znaleziono użytkownika") # Debug
                raise serializers.ValidationError("Nie znaleziono użytkownika")
                
        except Exception as e:
            print(f"Inny błąd: {str(e)}") # Debug
            raise serializers.ValidationError(str(e))

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uidb64 = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError('Hasła nie są identyczne')
        return data  