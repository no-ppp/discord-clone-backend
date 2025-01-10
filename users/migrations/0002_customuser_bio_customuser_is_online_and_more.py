# Generated by Django 5.1.4 on 2025-01-10 18:06

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='bio',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='last_online',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='customuser',
            name='privacy_settings',
            field=models.JSONField(blank=True, default=dict, help_text='Ustawienia prywatności użytkownika'),
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(default='friend_request', max_length=50),
        ),
        migrations.AlterField(
            model_name='notification',
            name='related_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='users.friendrequest'),
        ),
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_friendships', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friendships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'friend')},
            },
        ),
        migrations.AddField(
            model_name='customuser',
            name='friends',
            field=models.ManyToManyField(related_name='user_friends', through='users.Friendship', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='UserBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('blocked_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_blocks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'blocked_user')},
            },
        ),
    ]
