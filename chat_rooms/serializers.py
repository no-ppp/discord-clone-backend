from rest_framework import serializers
from .models import ChatRoom
from users.serializers import UserSerializer

class ChatRoomSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'description', 'created_at', 'members']
        read_only_fields = ['id', 'created_at']

class ChatRoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['name', 'description'] 