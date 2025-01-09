from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatRoom
from .serializers import ChatRoomSerializer, ChatRoomCreateSerializer

class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ChatRoomCreateSerializer
        return ChatRoomSerializer

    def perform_create(self, serializer):
        chat_room = serializer.save()
        chat_room.members.add(self.request.user)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        chat_room = self.get_object()
        chat_room.members.add(request.user)
        return Response({'status': 'dołączono do pokoju'})

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        chat_room = self.get_object()
        chat_room.members.remove(request.user)
        return Response({'status': 'opuszczono pokój'})
