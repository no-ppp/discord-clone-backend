from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.utils import timezone
from notifications.models import Notification

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
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    is_online = models.BooleanField(default=False)
    last_online = models.DateTimeField(default=timezone.now)
    friends = models.ManyToManyField(
        'self',
        through='Friendship',
        through_fields=('user', 'friend'),
        symmetrical=False,
        related_name='user_friends'
    )
    
    # Prywatność
    privacy_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Ustawienia prywatności użytkownika"
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('busy', 'Busy'),
        ('away', 'Away')
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='offline'
    )
    is_online = models.BooleanField(default=False)
    last_online = models.DateTimeField(default=timezone.now)

    def set_status(self, status):
        if status in dict(self.STATUS_CHOICES):
            self.status = status
            self.is_online = (status == 'online')
            self.last_online = timezone.now()
            self.save(update_fields=['status', 'is_online', 'last_online'])

    def go_online(self):
        """Ustawia użytkownika jako online"""
        self.set_status('online')

    def go_offline(self):
        """Ustawia użytkownika jako offline"""
        self.set_status('offline')

    def set_busy(self):
        """Ustawia status jako zajęty"""
        self.set_status('busy')

    def set_away(self):
        """Ustawia status jako away"""
        self.set_status('away')

    def __str__(self):
        return self.email

class Friendship(models.Model):
    STATUS_CHOICES = [
        ('active', 'Aktywna'),
        ('blocked', 'Zablokowana'),
        ('unfriended', 'Zakończona')
    ]

    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='friendships'
    )
    friend = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='friend_friendships'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Opcjonalne pola dla lepszego zarządzania relacją
    blocked_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='blocked_friendships'
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Prywatne notatki o znajomym"
    )

    class Meta:
        unique_together = ('user', 'friend')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['friend', 'status']),
        ]

    def __str__(self):
        return f"{self.user} -> {self.friend} ({self.status})"

    def block(self, blocked_by_user):
        """Blokuje znajomość"""
        self.status = 'blocked'
        self.blocked_by = blocked_by_user
        self.save()

    def unblock(self):
        """Odblokowuje znajomość"""
        self.status = 'active'
        self.blocked_by = None
        self.save()

    def unfriend(self):
        """Kończy znajomość"""
        self.status = 'unfriended'
        self.save()

    @classmethod
    def get_friends(cls, user):
        """Zwraca aktywnych znajomych użytkownika"""
        return CustomUser.objects.filter(
            friendships__friend=user,
            friendships__status='active'
        ).only(
            'id', 'email', 'username', 'avatar', 
            'status', 'is_online', 'last_online'
        )

    @classmethod
    def are_friends(cls, user1, user2):
        """Sprawdza czy użytkownicy są znajomymi"""
        return cls.objects.filter(
            user=user1,
            friend=user2,
            status='active'
        ).exists()

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Notification.create_friend_request_notification(self)

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"

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
