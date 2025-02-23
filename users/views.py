from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, OpenApiExample
from .models import FriendRequest, CustomUser as User, Friendship
from notifications.models import Notification
from .serializers import UserSerializer, FriendRequestSerializer, FriendSerializer, LoginSerializer, FriendshipStatusSerializer, LogoutSerializer
from django.shortcuts import get_object_or_404
import logging
from django.db.models import Q
from .docs import LOGIN_DOCS, REGISTER_DOCS, LOGOUT_DOCS, SEND_FRIEND_REQUEST_DOCS, ACCEPT_FRIEND_REQUEST_DOCS, PASSWORD_RESET_DOCS, PASSWORD_RESET_CONFIRM_DOCS, NOTIFICATION_LIST_DOCS, USER_LIST_DOCS, USER_RETRIEVE_DOCS, PENDING_REQUESTS_DOCS, REJECT_FRIEND_REQUEST_DOCS, ME_DOCS, GET_FRIEND_REQUEST_DOCS, GET_FRIENDS_DOCS, FRIENDSHIP_STATUS_DOCS, MARK_READ_DOCS, MARK_ALL_READ_DOCS, UNREAD_COUNT_DOCS, UPDATE_STATUS_DOCS, REMOVE_FRIEND_DOCS

User = get_user_model()
logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(**LOGIN_DOCS)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(**REGISTER_DOCS)
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
    permission_classes = [AllowAny]
    serializer_class = LogoutSerializer

    @extend_schema(**LOGOUT_DOCS)
    def post(self, request):
        print("Received logout request")
        print("Request data:", request.data)
        
        serializer = self.serializer_class(data=request.data)
        
        try:
            if serializer.is_valid():
                print("Serializer valid")
                return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
            else:
                print("Serializer errors:", serializer.errors)
                # Zawsze wyloguj użytkownika lokalnie, nawet jeśli token jest nieprawidłowy
                return Response(
                    {"message": "Logged out locally", "errors": serializer.errors}, 
                    status=status.HTTP_200_OK  # Zmieniamy na 200 OK
                )
        except Exception as e:
            print("Unexpected error:", str(e))
            return Response(
                {"message": "Logged out locally", "error": str(e)},
                status=status.HTTP_200_OK  # Zmieniamy na 200 OK
            )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(**USER_LIST_DOCS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**USER_RETRIEVE_DOCS)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(**SEND_FRIEND_REQUEST_DOCS)
    @action(detail=True, methods=['POST'], url_path='send-friend-request')
    def send_friend_request(self, request, pk=None):
        try:
            receiver = self.get_object()
            sender = request.user

            # Sprawdź czy nie wysyłasz do siebie
            if sender == receiver:
                return Response(
                    {'error': 'Nie możesz wysłać zaproszenia do samego siebie'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Sprawdź czy zaproszenie już nie istnieje
            existing_request = FriendRequest.objects.filter(
                sender=sender,
                receiver=receiver,
                status=FriendRequest.PENDING
            ).first()

            if existing_request:
                return Response(
                    {'error': 'Zaproszenie już zostało wysłane'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Sprawdź czy nie są już znajomymi
            if Friendship.objects.filter(user=sender, friend=receiver).exists():
                return Response(
                    {'error': 'Jesteście już znajomymi'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            friend_request = FriendRequest.objects.create(
                sender=sender, 
                receiver=receiver,
                status=FriendRequest.PENDING
            ) # it automatically creates notification bc
              # of the Notification.create_friend_request_notification()
              # method in the FriendRequest model

            return Response(
                {'message': 'Zaproszenie wysłane'},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(**PENDING_REQUESTS_DOCS)
    @action(detail=False, methods=['GET'], url_path='pending-requests')
    def pending_requests(self, request):
        pending_requests = FriendRequest.objects.filter(
            receiver=request.user,
            status=FriendRequest.PENDING
        )
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data)

    @extend_schema(**ACCEPT_FRIEND_REQUEST_DOCS)
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

            Notification.objects.filter(
                related_request=friend_request,
                notification_type='friend_request'
            ).delete()

            Notification.create_friend_request_notification(friend_request)          
            
            return Response({'message': 'Zaproszenie zaakceptowane'},
                            status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(**REJECT_FRIEND_REQUEST_DOCS)
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

    @extend_schema(**ME_DOCS)
    @action(detail=False, methods=['GET'])
    def me(self, request):
        """
        Zwraca dane zalogowanego użytkownika
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(**GET_FRIEND_REQUEST_DOCS)
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

    @extend_schema(**GET_FRIENDS_DOCS)
    @action(detail=True, methods=['GET'], url_path='friends')
    def get_friends(self, request, pk=None):
        user = self.get_object()
        friends = Friendship.get_friends(user)
        serializer = FriendSerializer(friends, many=True)
        return Response(serializer.data)
    

    @extend_schema(**FRIENDSHIP_STATUS_DOCS)
    @action(detail=True, methods=['GET'], url_path='friendship-status')
    def get_friendship_status(self, request, pk=None):
        other_user = self.get_object()
        try:
            friendship = Friendship.objects.get(
                user=request.user,
                friend=other_user
            )
        except Friendship.DoesNotExist:
            friendship = None
        
        serializer = FriendshipStatusSerializer(friendship)
        return Response(serializer.data)

    @extend_schema(**UPDATE_STATUS_DOCS)
    @action(detail=True, methods=['POST'], url_path='update-status')
    def update_status(self, request, pk=None):
        user = self.get_object()
        status = request.data.get('status')
        
        if status not in dict(User.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=400
            )

        user.set_status(status)
        return Response({
            'status': user.status,
            'is_online': user.is_online,
            'last_online': user.last_online
        })
    
    @extend_schema(**REMOVE_FRIEND_DOCS)
    @action(detail=True, methods=['POST'], url_path='remove-friend')
    def remove_friend(self, request, pk=None):
        """Usuwa użytkownika ze znajomych"""
        user_to_remove = self.get_object()
        
        # Usuń relację w obie strony
        Friendship.objects.filter(
            (Q(user=request.user, friend=user_to_remove) |
             Q(user=user_to_remove, friend=request.user)),
            status='active'
        ).delete()
        FriendRequest.objects.filter(
            sender=request.user,
            receiver=user_to_remove,
            status=FriendRequest.ACCEPTED
        ).delete()
        
        return Response({"message": "Friend removed successfully"}, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(**PASSWORD_RESET_DOCS)
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

    @extend_schema(**PASSWORD_RESET_CONFIRM_DOCS)
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Hasło zostało zmienione pomyślnie'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

