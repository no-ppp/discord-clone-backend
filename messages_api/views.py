from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Message
from .serializers import MessageSerializer, MessageCreateSerializer

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def get_queryset(self):
        chat_room_id = self.request.query_params.get('chat_room', None)
        queryset = Message.objects.all()
        if chat_room_id:
            queryset = queryset.filter(chat_room_id=chat_room_id)
        return queryset
