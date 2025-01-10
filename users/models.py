from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email jest wymagany')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    friends = models.ManyToManyField(
        'self',
        through='Friendship',
        symmetrical=False,
        related_name='user_friends'
    )
    last_online = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=False)
    
    # Prywatność
    privacy_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Ustawienia prywatności użytkownika"
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Friendship(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friendships')
    friend = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='friend_friendships')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'friend')

class FriendRequest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'Oczekujące'),
        (ACCEPTED, 'Zaakceptowane'),
        (REJECTED, 'Odrzucone'),
    ]

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_friend_requests'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"

    def create_notification(self):
        """Automatycznie tworzy odpowiednią notyfikację"""
        if self.status == self.PENDING:
            text = f"{self.sender.email} wysłał(a) Ci zaproszenie do znajomych"
            recipient = self.receiver
        elif self.status == self.ACCEPTED:
            text = f"{self.receiver.email} zaakceptował(a) Twoje zaproszenie do znajomych"
            recipient = self.sender
        else:  # REJECTED
            text = f"{self.receiver.email} odrzucił(a) Twoje zaproszenie do znajomych"
            recipient = self.sender

        Notification.objects.create(
            recipient=recipient,
            related_request=self,
            text=text
        )

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    related_request = models.ForeignKey(
        FriendRequest,
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

class UserBlock(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='user_blocks'
    )
    blocked_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='blocked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'blocked_user')
