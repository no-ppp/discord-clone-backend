from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings

class CustomUserManager(BaseUserManager):
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
    
    email = models.EmailField('email address', unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    status = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=150, unique=True)  

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username']  

    objects = CustomUserManager()

    # Pole do zarządzania znajomymi
    friends = models.ManyToManyField(
        'self',
        through='FriendRequest',
        symmetrical=False,
        related_name='friend_requests'
    )

    def __str__(self):
        return self.email

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

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"

class Notification(models.Model):
    FRIEND_REQUEST = 'friend_request'
    FRIEND_REQUEST_ACCEPTED = 'friend_request_accepted'
    FRIEND_REQUEST_REJECTED = 'friend_request_rejected'

    TYPE_CHOICES = [
        (FRIEND_REQUEST, 'Zaproszenie do znajomych'),
        (FRIEND_REQUEST_ACCEPTED, 'Zaakceptowane zaproszenie do znajomych'),
        (FRIEND_REQUEST_REJECTED, 'Odrzucone zaproszenie do znajomych'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at'] 
    
    def __str__(self):
        return f"{self.sender} -> {self.recipient} ({self.text})"
