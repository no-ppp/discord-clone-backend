from django.db import models
from django.conf import settings
# Create your models here.
class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
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
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notyfikacja dla {self.recipient}: {self.text}"

    @classmethod
    def create_friend_request_notification(cls, friend_request):
        """Tworzy notyfikację na podstawie friend request"""
        if friend_request.status == friend_request.PENDING:
            text = f"{friend_request.sender.email} wysłał(a) Ci zaproszenie do znajomych"
            recipient = friend_request.receiver
        elif friend_request.status == friend_request.ACCEPTED:
            text = f"{friend_request.receiver.email} zaakceptował(a) Twoje zaproszenie do znajomych"
            recipient = friend_request.sender
        else:
            text = f"{friend_request.receiver.email} odrzucił(a) Twoje zaproszenie do znajomych"
            recipient = friend_request.sender
        return cls.objects.create(
            recipient=recipient, text=text)
