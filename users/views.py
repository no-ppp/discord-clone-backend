from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample
from .models import FriendRequest, Notification, CustomUser as User, Friendship
from .serializers import UserSerializer, FriendRequestSerializer, NotificationSerializer, FriendSerializer
from rest_framework import serializers
from django.shortcuts import get_object_or_404
import logging
from django.db.models import Q

User = get_user_model()
logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Logowanie użytkownika",
        description="Loguje użytkownika i zwraca tokeny JWT oraz dane użytkownika",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string'},
                },
                'required': ['email', 'password']
            }
        },
        responses={
            200: OpenApiResponse(
                description="Pomyślne logowanie",
                response={
                    'type': 'object',
                    'properties': {
                        'tokens': {
                            'type': 'object',
                            'properties': {
                                'access': {'type': 'string'},
                                'refresh': {'type': 'string'},
                            }
                        },
                        'user': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'email': {'type': 'string'},
                                'avatar': {'type': 'string', 'nullable': True},
                                'status': {'type': 'string', 'nullable': True},
                            }
                        }
                    }
                }
            ),
            400: OpenApiResponse(description="Błędne dane logowania"),
            401: OpenApiResponse(description="Nieprawidłowe dane uwierzytelniające")
        }
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'Proszę podać email i hasło'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(email=email, password=password)

        if not user:
            return Response(
                {'error': 'Nieprawidłowy email lub hasło'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': {
                'id': user.id,
                'email': user.email,
                'avatar': user.avatar.url if user.avatar else None,
                'status': user.status,
            }
        })

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Rejestracja użytkownika",
        description="Tworzy nowe konto użytkownika",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                    'password': {'type': 'string'},
                    'password2': {'type': 'string'},
                },
                'required': ['email', 'password', 'password2']
            }
        },
        responses={
            201: OpenApiResponse(description="Użytkownik został utworzony"),
            400: OpenApiResponse(description="Błędne dane rejestracji")
        }
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'message': 'Użytkownik został zarejestrowany pomyślnie'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(
        summary="Wylogowanie użytkownika",
        description="Wylogowuje użytkownika i unieważnia token",
        request=LogoutSerializer,
        responses={
            200: OpenApiResponse(description="Pomyślne wylogowanie"),
            400: OpenApiResponse(description="Błąd wylogowania")
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Pomyślnie wylogowano'})
        except Exception:
            return Response(
                {'error': 'Błąd wylogowania'},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Lista użytkowników",
        description="Zwraca listę wszystkich użytkowników"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Szczegóły użytkownika",
        description="Zwraca szczegółowe informacje o użytkowniku"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Wysyłanie zaproszenia do znajomych",
        description="Wysyła zaproszenie do znajomych do wybranego użytkownika",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID użytkownika, do którego wysyłamy zaproszenie"
            ),
        ],
        request=None,  # Nie potrzebujemy body w request
        responses={
            200: OpenApiResponse(
                description="Zaproszenie wysłane",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'Zaproszenie wysłane'
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description="Błąd wysyłania zaproszenia",
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Nie możesz wysłać zaproszenia do samego siebie'
                        }
                    }
                }
            ),
            404: OpenApiResponse(description="Użytkownik nie znaleziony")
        }
    )
    @action(detail=True, methods=['POST'], url_path='send-friend-request')
    def send_friend_request(self, request, pk=None):
        receiver = self.get_object()
        sender = request.user

        if sender == receiver:
            return Response(
                {'error': 'Nie możesz wysłać zaproszenia do samego siebie'},
                status=status.HTTP_400_BAD_REQUEST
            )

        friend_request = FriendRequest.objects.create(sender=sender, receiver=receiver)
        friend_request.create_notification()  # Automatycznie tworzy notyfikację
        return Response({'message': 'Zaproszenie wysłane'})

    @extend_schema(
        summary="Oczekujące zaproszenia",
        description="Zwraca listę oczekujących zaproszeń do znajomych"
    )
    @action(detail=False, methods=['GET'], url_path='pending-requests')
    def pending_requests(self, request):
        pending_requests = FriendRequest.objects.filter(
            receiver=request.user,
            status=FriendRequest.PENDING
        )
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Akceptacja zaproszenia",
        description="Akceptuje zaproszenie do znajomych od wybranego użytkownika",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=int,
                location=OpenApiParameter.PATH,
                description="ID użytkownika, którego zaproszenie akceptujemy"
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Zaproszenie zaakceptowane",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {
                            'type': 'string',
                            'example': 'Zaproszenie zaakceptowane'
                        }
                    }
                }
            ),
            404: OpenApiResponse(
                description="Nie znaleziono zaproszenia",
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string',
                            'example': 'Nie znaleziono oczekującego zaproszenia'
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description="Błąd podczas akceptacji zaproszenia",
                response={
                    'type': 'object',
                    'properties': {
                        'error': {
                            'type': 'string'
                        }
                    }
                }
            )
        }
    )
    @action(detail=True, methods=['POST'], url_path='accept-friend-request')
    def accept_friend_request(self, request, pk=None):
        try:
            sender = self.get_object()
            friend_request = FriendRequest.objects.filter(
                sender=sender,
                receiver=request.user,
                status=FriendRequest.PENDING
            ).first()

            if not friend_request:
                return Response(
                    {'error': 'Nie znaleziono oczekującego zaproszenia'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Akceptuj zaproszenie
            friend_request.status = FriendRequest.ACCEPTED
            friend_request.save()
            
            # Utwórz relację znajomości w obie strony
            Friendship.objects.create(user=request.user, friend=sender)
            Friendship.objects.create(user=sender, friend=request.user)
            
            # Stwórz powiadomienie
            friend_request.create_notification()
            
            return Response({'message': 'Zaproszenie zaakceptowane'})
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Odrzucenie zaproszenia",
        description="Odrzuca zaproszenie do znajomych"
    )
    @action(detail=True, methods=['POST'], url_path='reject-friend-request')
    def reject_friend_request(self, request, pk=None):
        try:
            all_users = User.objects.all()
            logger.info(f"Dostępni użytkownicy: {list(all_users.values('id', 'email'))}")
            logger.info(f"Szukamy użytkownika o ID: {pk}")
            logger.info(f"Aktualny użytkownik: {request.user.id} ({request.user.email})")

            sender = get_object_or_404(User, pk=pk)
            
            # Sprawdź wszystkie zaproszenia
            all_requests = FriendRequest.objects.filter(
                sender=sender,
                receiver=request.user
            )
            logger.info(f"Znalezione zaproszenia: {list(all_requests.values())}")
            
            friend_request = all_requests.filter(status=FriendRequest.PENDING).first()
            
            if not friend_request:
                return Response(
                    {'error': 'Nie znaleziono oczekującego zaproszenia'},
                    status=status.HTTP_404_NOT_FOUND
                )

            friend_request.status = FriendRequest.REJECTED
            friend_request.save()
            
            return Response({'message': 'Zaproszenie odrzucone'})
            
        except User.DoesNotExist:
            logger.error(f"Nie znaleziono użytkownika o ID: {pk}")
            return Response(
                {'error': f'Nie znaleziono użytkownika o ID: {pk}'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Błąd podczas odrzucania zaproszenia: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        summary="Dane zalogowanego użytkownika",
        description="Zwraca szczegółowe informacje o zalogowanym użytkowniku",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Brak autoryzacji")
        }
    )
    @action(detail=False, methods=['GET'])
    def me(self, request):
        """
        Zwraca dane zalogowanego użytkownika
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Sprawdź pojedyncze zaproszenie",
        description="Zwraca szczegóły konkretnego zaproszenia do znajomych",
        responses={
            200: FriendRequestSerializer,
            404: OpenApiResponse(description="Nie znaleziono zaproszenia")
        }
    )
    @action(detail=True, methods=['GET'], url_path='friend-request')
    def get_friend_request(self, request, pk=None):
        other_user = self.get_object()
        
        # Szukamy zaproszenia między zalogowanym użytkownikiem a wybranym użytkownikiem
        friend_request = FriendRequest.objects.filter(
            (Q(sender=request.user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=request.user))
        ).first()
        
        if not friend_request:
            return Response(
                {'error': 'Nie znaleziono zaproszenia'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data)

    @extend_schema(
        summary="Lista znajomych użytkownika",
        description="Zwraca listę aktywnych znajomych użytkownika"
    )
    @action(detail=True, methods=['GET'], url_path='friends')
    def get_friends(self, request, pk=None):
        user = self.get_object()
        friends = Friendship.get_friends(user)
        serializer = FriendSerializer(friends, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Szczegóły znajomości",
        description="Zwraca szczegóły relacji znajomości między dwoma użytkownikami"
    )
    @action(detail=True, methods=['GET'], url_path='friends')
    def get_friendship_status(self, request, pk=None):
        other_user = self.get_object()
        
        try:
            friendship = Friendship.objects.get(
                user=request.user,
                friend=other_user
            )
            
            return Response({
                'status': friendship.status,
                'since': friendship.created_at,
                'last_updated': friendship.updated_at,
                'is_blocked': friendship.status == 'blocked',
                'blocked_by': friendship.blocked_by.id if friendship.blocked_by else None
            })
        except Friendship.DoesNotExist:
            return Response({
                'status': 'not_friends',
                'is_blocked': False
            })

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Żądanie resetowania hasła",
        description="Wysyła email z linkiem do resetowania hasła",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'format': 'email'},
                },
                'required': ['email']
            }
        },
        responses={
            200: OpenApiResponse(
                description="Email z linkiem do resetowania hasła został wysłany"
            ),
            400: OpenApiResponse(description="Błędny email")
        }
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Link do resetowania hasła został wysłany na podany adres email'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Potwierdzenie resetowania hasła",
        description="Ustawia nowe hasło po resetowaniu",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string'},
                    'uidb64': {'type': 'string'},
                    'password': {'type': 'string'},
                    'password2': {'type': 'string'},
                },
                'required': ['token', 'uidb64', 'password', 'password2']
            }
        },
        responses={
            200: OpenApiResponse(description="Hasło zostało zmienione"),
            400: OpenApiResponse(description="Błędne dane"),
            404: OpenApiResponse(description="Nieprawidłowy token lub użytkownik")
        }
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Hasło zostało zmienione pomyślnie'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_value_regex = '[0-9]+'

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @extend_schema(
        summary="Lista notyfikacji",
        description="Zwraca listę notyfikacji dla zalogowanego użytkownika",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="ID notyfikacji"
            ),
        ],
        responses={
            200: NotificationSerializer(many=True),
            401: OpenApiResponse(description="Brak autoryzacji")
        }
    )
    def list(self, request):
        notifications = self.get_queryset()
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Oznacz jako przeczytane",
        description="Oznacza notyfikację jako przeczytaną"
    )
    @action(detail=True, methods=['POST'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'ok'})

    @extend_schema(
        summary="Oznacz wszystkie jako przeczytane",
        description="Oznacza wszystkie notyfikacje jako przeczytane"
    )
    @action(detail=False, methods=['POST'], url_path='mark-all-read')
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'ok'})

    @extend_schema(
        summary="Liczba nieprzeczytanych",
        description="Zwraca liczbę nieprzeczytanych notyfikacji"
    )
    @action(detail=False, methods=['GET'], url_path='unread-count')
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})