from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .docs import GET_NOTIFICATIONS_DOCS, MARK_AS_READ_ALL_DOCS, MARK_AS_READ_DOCS, DELETE_NOTIFICATION_DOCS

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    @extend_schema(**GET_NOTIFICATIONS_DOCS)
    def get_queryset(self):
        return Notification.objects.filter(
            recipient = self.request.user
        ).order_by('-created_at')
    
    @extend_schema(**MARK_AS_READ_DOCS)
    @action(detail=True, methods=['POST'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        if notification.auto_delete:
            notification.delete()
        else:
            notification.is_read = True
            notification.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='mark-as-read-all')
    @extend_schema(**MARK_AS_READ_ALL_DOCS)
    def mark_as_read_all(self, request):
        notifications = self.get_object()
        notifications.update(is_read=True)
        notifications.save()
        return Response(status=status.HTTP_200_OK)
    
    @extend_schema(**DELETE_NOTIFICATION_DOCS)
    @action(detail=True, methods=['DELETE'], url_path='delete')
    def delete_notification(self, request, pk=None):
        notification = self.get_queryset()
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
