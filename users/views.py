from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from .models import FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer

User = get_user_model()

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

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Wylogowanie użytkownika",
        description="Wylogowuje użytkownika i unieważnia token",
        responses={
            200: OpenApiResponse(description="Pomyślne wylogowanie"),
            401: OpenApiResponse(description="Brak autoryzacji")
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
        responses={
            200: OpenApiResponse(description="Zaproszenie wysłane"),
            400: OpenApiResponse(description="Błąd wysyłania zaproszenia")
        }
    )
    @action(detail=True, methods=['POST'])
    def send_friend_request(self, request, pk=None):
        receiver = self.get_object()
        sender = request.user

        if sender == receiver:
            return Response(
                {'error': 'Nie możesz wysłać zaproszenia do samego siebie'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if FriendRequest.objects.filter(sender=sender, receiver=receiver).exists():
            return Response(
                {'error': 'Zaproszenie już zostało wysłane'},
                status=status.HTTP_400_BAD_REQUEST
            )

        FriendRequest.objects.create(sender=sender, receiver=receiver)
        return Response({'message': 'Zaproszenie wysłane'})

    @extend_schema(
        summary="Lista znajomych",
        description="Zwraca listę znajomych zalogowanego użytkownika"
    )
    @action(detail=False, methods=['GET'])
    def my_friends(self, request):
        user = request.user
        friends = User.objects.filter(
            sent_friend_requests__receiver=user,
            sent_friend_requests__status=FriendRequest.ACCEPTED
        ) | User.objects.filter(
            received_friend_requests__sender=user,
            received_friend_requests__status=FriendRequest.ACCEPTED
        )
        serializer = self.get_serializer(friends, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Oczekujące zaproszenia",
        description="Zwraca listę oczekujących zaproszeń do znajomych"
    )
    @action(detail=False, methods=['GET'])
    def pending_requests(self, request):
        pending_requests = FriendRequest.objects.filter(
            receiver=request.user,
            status=FriendRequest.PENDING
        )
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Akceptacja zaproszenia",
        description="Akceptuje zaproszenie do znajomych"
    )
    @action(detail=True, methods=['POST'])
    def accept_friend_request(self, request, pk=None):
        friend_request = FriendRequest.objects.filter(
            sender_id=pk,
            receiver=request.user,
            status=FriendRequest.PENDING
        ).first()

        if not friend_request:
            return Response(
                {'error': 'Nie znaleziono zaproszenia'},
                status=status.HTTP_404_NOT_FOUND
            )

        friend_request.status = FriendRequest.ACCEPTED
        friend_request.save()
        return Response({'message': 'Zaproszenie zaakceptowane'})

    @extend_schema(
        summary="Odrzucenie zaproszenia",
        description="Odrzuca zaproszenie do znajomych"
    )
    @action(detail=True, methods=['POST'])
    def reject_friend_request(self, request, pk=None):
        friend_request = FriendRequest.objects.filter(
            sender_id=pk,
            receiver=request.user,
            status=FriendRequest.PENDING
        ).first()

        if not friend_request:
            return Response(
                {'error': 'Nie znaleziono zaproszenia'},
                status=status.HTTP_404_NOT_FOUND
            )

        friend_request.status = FriendRequest.REJECTED
        friend_request.save()
        return Response({'message': 'Zaproszenie odrzucone'})

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
