from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer, FriendRequestSerializer


class NotificationSerializer(serializers.ModelSerializer):
    recipient = UserSerializer(read_only=True)
    related_request = FriendRequestSerializer(read_only=True)

    class Meta: 
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    
