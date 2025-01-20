from django.db import models
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
# Create your models here.
class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    related_request = models.ForeignKey(
        'users.FriendRequest',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_type = models.CharField(
        max_length=50,
        default='friend_request'
    )
    auto_delete = models.BooleanField(default=False)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notyfikacja dla {self.recipient}: {self.text}"
    
    def send_websocket_notification(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{self.recipient.id}',
            {
                'type': 'send_notification',
                'notification_id': self.id,
                'text': self.text,
                'sender': self.sender.email if self.sender else None,
                'created_at': self.created_at.isoformat(),
                'notification_type': self.notification_type,
                'auto_delete': self.auto_delete
            }
        )

    @classmethod
    def create_friend_request_notification(cls, friend_request):
        """Tworzy notyfikację na podstawie friend request"""
        if friend_request.status == friend_request.PENDING:
            text = f"{friend_request.sender.email} wysłał(a) Ci zaproszenie do znajomych"
            auto_delete = False
            recipient = friend_request.receiver
            sender = friend_request.sender
        elif friend_request.status == friend_request.ACCEPTED:
            text = f"{friend_request.receiver.email} zaakceptował(a) Twoje zaproszenie do znajomych"
            auto_delete = True
            recipient = friend_request.sender
            sender = friend_request.receiver
        else:
            text = f"{friend_request.receiver.email} odrzucił(a) Twoje zaproszenie do znajomych"
            auto_delete = True
            recipient = friend_request.sender
            sender = friend_request.receiver
        notification = cls.objects.create(
            recipient=recipient, 
            text=text, 
            sender=sender,
            related_request=friend_request,
            auto_delete=auto_delete
        )
        notification.send_websocket_notification()
        return notification
