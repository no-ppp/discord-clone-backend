from django.contrib import admin
from .models import CustomUser, FriendRequest, Notification

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_staff', 'is_active')
    search_fields = ('email',)

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'status', 'created_at', 'is_read')
    list_filter = ('status', 'is_read')
    search_fields = ('sender__email', 'receiver__email')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient','text', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('recipient__email', 'text')
