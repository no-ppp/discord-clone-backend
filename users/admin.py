from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Friendship, FriendRequest, Notification, UserBlock

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'username', 'is_staff', 'is_active', 'is_online', 'last_online')
    list_filter = ('is_staff', 'is_active', 'is_online')
    search_fields = ('email', 'username')
    ordering = ('-last_online',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informacje osobiste', {'fields': ('username', 'avatar', 'status', 'bio')}),
        ('Status', {'fields': ('is_online', 'last_online')}),
        ('Uprawnienia', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Prywatność', {'fields': ('privacy_settings',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'friend__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at', 'is_read')
    list_filter = ('status', 'is_read', 'created_at')
    search_fields = ('sender__email', 'receiver__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('sender', 'receiver', 'status')
        }),
        ('Status odczytu', {
            'fields': ('is_read',)
        }),
        ('Daty', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'text', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type', 'created_at')
    search_fields = ('recipient__email', 'text')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Podstawowe informacje', {
            'fields': ('recipient', 'text', 'notification_type')
        }),
        ('Powiązane', {
            'fields': ('related_request',)
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )

@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ('user', 'blocked_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'blocked_user__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    readonly_fields = ('created_at',)
